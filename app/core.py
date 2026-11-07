"""Core pipeline with advanced hooks (deskew, inpaint, super-res, RAG, PSNR, table grouping)."""
import os, re, logging
from typing import Optional, Dict, Any
from pathlib import Path
import cv2, numpy as np, pytesseract
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from difflib import SequenceMatcher
from .advanced import deskew_and_detect_rotation, group_into_table_cells, inpaint_text_regions, simple_super_resolution, protected_region_psnr, SimpleRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GLOSSARY = {"Placement": "位置", "Quantity": "数量", "Yards": "码", "Beige": "米色", "Black": "黑色", "White": "白色", "Natural": "自然色", "Each": "个", "Clear": "透明", "Packaging": "包装", "N/A": "不适用", "Design pack image": "设计包装图"}
CHINESE_RE = re.compile(r"[\u4e00-\u9fff]")
rag = SimpleRAG()
for k,v in GLOSSARY.items(): rag.add(k,v)

def contains_chinese(t): return bool(CHINESE_RE.search(t))

class Translator:
    def __init__(self, backend="glossary", api_key=None, use_rag=True):
        self.backend = backend.lower()
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.use_rag = use_rag
    def translate(self, text):
        text = text.strip()
        if not text or contains_chinese(text): return None
        if self.use_rag: rag.retrieve(text)
        return self._qwen(text) if self.backend=="qwen" else self._glossary(text)
    def _glossary(self, text, threshold=0.70):
        if text in GLOSSARY: return GLOSSARY[text]
        best = max(((SequenceMatcher(None, text.lower(), k.lower()).ratio(), v) for k,v in GLOSSARY.items()), default=(0,None))
        return best[1] if best[0] >= threshold else None
    def _qwen(self, text):
        if not self.api_key: return self._glossary(text)
        try:
            import dashscope
            from dashscope import Generation
            dashscope.api_key = self.api_key
            resp = Generation.call(model="qwen-plus", messages=[{"role":"system","content":"Apparel translator. topstitch=明线. Output only Chinese."},{"role":"user","content":text}], result_format="message")
            if resp.status_code==200: return resp.output.choices[0].message.content.strip()
        except Exception as e: logger.error(e)
        return self._glossary(text)

def detect_design_pack_region(img, mask_path=None, auto_right_ratio=0.62):
    h,w = img.shape[:2]
    if mask_path and os.path.exists(mask_path):
        m = cv2.resize(cv2.imread(mask_path,0), (w,h))
        _, mask = cv2.threshold(m,127,255,cv2.THRESH_BINARY)
        ys,xs = np.where(mask>0)
        return mask, (int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())) if len(xs) else (0,0,0,0)
    x1=int(w*auto_right_ratio); mask=np.zeros((h,w),np.uint8); mask[5:int(h*0.55), x1:w-10]=255
    return mask, (x1,5,w-10,int(h*0.55))

def get_chinese_font(size=16):
    for p in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc","/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"]:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def adaptive_font_size(draw, text, max_w, max_h, base=16):
    low,high,best=8,base,8
    while low<=high:
        mid=(low+high)//2
        f=get_chinese_font(mid)
        bb=draw.textbbox((0,0),text,font=f)
        if bb[2]-bb[0]<=max_w and bb[3]-bb[1]<=max_h: best=mid; low=mid+1
        else: high=mid-1
    return get_chinese_font(best)

def process_techpack(input_path, output_path, mask_path=None, translator=None, conf_threshold=45.0, min_text_height=8, show_protected=True, enhance_contrast=False, deskew=False, super_res=False, use_inpaint=False, compute_metrics=True):
    if translator is None: translator=Translator()
    pil=Image.open(input_path).convert("RGB")
    original=pil.copy()
    if super_res and min(pil.size)<800: pil=simple_super_resolution(pil)
    if deskew: pil,_=deskew_and_detect_rotation(pil)
    if enhance_contrast: pil=ImageEnhance.Contrast(pil).enhance(1.4)
    img_cv=cv2.cvtColor(np.array(pil),cv2.COLOR_RGB2BGR)
    design_mask, design_bbox=detect_design_pack_region(img_cv, mask_path)
    h,w=design_mask.shape
    data=pytesseract.image_to_data(pil, lang="eng", output_type=pytesseract.Output.DICT)
    boxes,flagged=[],[]
    for i in range(len(data["text"])):
        try: conf=float(data["conf"][i])
        except: continue
        text=data["text"][i].strip()
        if not text: continue
        x,y,bw,bh=data["left"][i],data["top"][i],data["width"][i],data["height"][i]
        cx,cy=x+bw//2,y+bh//2
        if not (0<=cy<h and 0<=cx<w) or design_mask[cy,cx]>0: continue
        if bh<min_text_height: flagged.append({"text":text,"reason":"too_small"}); continue
        if conf<conf_threshold: flagged.append({"text":text,"reason":"low_confidence"}); continue
        if bw>w*0.6 or text.lower() in {"page","page 1"}: flagged.append({"text":text,"reason":"watermark"}); continue
        if contains_chinese(text): continue
        boxes.append({"text":text,"x":x,"y":y,"w":bw,"h":bh,"conf":conf})
    table_rows=group_into_table_cells(boxes)
    if use_inpaint and boxes: pil=inpaint_text_regions(pil, boxes)
    out=pil.copy(); draw=ImageDraw.Draw(out)
    translated=0; translations=[]
    for b in boxes:
        trans=translator.translate(b["text"])
        if not trans: flagged.append({"text":b["text"],"reason":"no_translation"}); continue
        font=adaptive_font_size(draw, trans, b["w"]+4, b["h"]+2)
        if not use_inpaint: draw.rectangle([b["x"]-1,b["y"]-1,b["x"]+b["w"]+2,b["y"]+b["h"]+2], fill="white")
        draw.text((b["x"],b["y"]), trans, fill="black", font=font)
        translated+=1; translations.append({"original":b["text"],"translated":trans}); rag.add(b["text"], trans)
    if design_bbox[2]>design_bbox[0]:
        x1,y1,x2,y2=design_bbox
        region=original.crop((x1,y1,x2,y2))
        out.paste(region, (x1,y1))
        if show_protected:
            draw=ImageDraw.Draw(out)
            draw.rectangle(design_bbox, outline="red", width=3)
            draw.text((x1+8,y1+8), "PROTECTED", fill="red", font=get_chinese_font(12))
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    out.save(output_path, quality=95)
    metrics={}
    if compute_metrics and design_bbox[2]>design_bbox[0]:
        metrics["protected_psnr"]=protected_region_psnr(original, out, design_bbox)
    return {"translated":translated, "flagged":flagged, "table_rows":len(table_rows), "protected_bbox":design_bbox, "translations":translations, "metrics":metrics}
