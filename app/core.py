"""
Production-oriented Tech Pack Translator
Designed for Crystal Group–style global apparel operations.
"""
import os
import logging
from typing import Optional, Tuple, Dict, Any
from pathlib import Path
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw, ImageFont
from difflib import SequenceMatcher

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

GLOSSARY = {
    "Style Name:": "款式名称:",
    "Brand Name/Logo:": "品牌名称/标志:",
    "Designer's Name:": "设计师姓名:",
    "Style Number:": "款号:",
    "Season/Release:": "季节/发布:",
    "Fit Block Reference:": "版型参考:",
    "Factory Details:": "工厂详情:",
    "Target Volume:": "目标产量:",
    "Size Range/Sample:": "尺码范围/样品:",
    "Contact Information:": "联系信息:",
    "Pattern File Name:": "纸样文件名:",
    "Colorways:": "配色:",
    "Product Category:": "产品类别:",
    "Style Description:": "款式描述:",
    "Description": "描述",
    "Placement": "位置",
    "Color Details": "颜色详情",
    "Quantity": "数量",
    "Cost": "成本",
    "Unit of Measure": "计量单位",
    "Main Fabric": "主面料",
    "Blue Light": "浅蓝",
    "Mocha Mousse": "摩卡慕斯",
    "Ultimate Gray": "终极灰",
    "As Per Requirement": "按要求",
    "Yards": "码",
    "All Seams": "所有缝线",
    "DTM": "染整匹配",
    "Armholes": "袖窿",
    "Beige": "米色",
    "Back Neck": "后领",
    "White": "白色",
    "Black": "黑色",
    "Natural": "自然色",
    "Each": "个",
    "Clear": "透明",
    "Packaging": "包装",
    "N/A": "不适用",
    "USE HEAVY THREAD FOR ALL TOPSTITCHING": "所有明线使用重线",
    "SINGLE NEEDLE TOPSTITCH": "单针明线",
    "ZIG ZAG TOPSTITCH": "之字明线",
    "DOUBLE NEEDLE TOPSTITCH": "双针明线",
    "Design pack image": "设计包装图",
    "Additional Notes & Comments:": "附加备注与评论:",
}

class Translator:
    def __init__(self, backend: str = "glossary", api_key: Optional[str] = None):
        self.backend = backend
        self.api_key = api_key or os.getenv("TRANSLATION_API_KEY")

    def translate(self, text: str) -> Optional[str]:
        text = text.strip()
        if not text:
            return None
        if self.backend == "glossary":
            return self._glossary(text)
        return self._glossary(text)  # fallback; extend for DeepL/OpenAI

    def _glossary(self, text: str, threshold: float = 0.70) -> Optional[str]:
        if text in GLOSSARY:
            return GLOSSARY[text]
        best_ratio, best = 0.0, None
        for k, v in GLOSSARY.items():
            ratio = SequenceMatcher(None, text.lower(), k.lower()).ratio()
            if ratio > best_ratio:
                best_ratio, best = ratio, v
        return best if best_ratio >= threshold else None

def detect_design_pack_region(img, mask_path=None, auto_right_ratio=0.62):
    h, w = img.shape[:2]
    if mask_path and os.path.exists(mask_path):
        mask_img = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        mask_img = cv2.resize(mask_img, (w, h))
        _, mask = cv2.threshold(mask_img, 127, 255, cv2.THRESH_BINARY)
        ys, xs = np.where(mask > 0)
        bbox = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())) if len(xs) else (0, 0, 0, 0)
        return mask, bbox
    x1 = int(w * auto_right_ratio)
    y1, x2, y2 = 5, w - 10, int(h * 0.55)
    mask = np.zeros((h, w), dtype=np.uint8)
    mask[y1:y2, x1:x2] = 255
    return mask, (x1, y1, x2, y2)

def get_chinese_font(size=16):
    candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()

def process_techpack(input_path, output_path, mask_path=None, translator=None, conf_threshold=40.0, show_protected=True):
    if translator is None:
        translator = Translator()
    pil_img = Image.open(input_path).convert("RGB")
    img_cv = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    design_mask, design_bbox = detect_design_pack_region(img_cv, mask_path)
    data = pytesseract.image_to_data(pil_img, lang="eng", output_type=pytesseract.Output.DICT)
    boxes = []
    for i in range(len(data["text"])):
        try:
            conf = float(data["conf"][i])
        except (ValueError, TypeError):
            continue
        text = data["text"][i].strip()
        if conf < conf_threshold or not text:
            continue
        x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
        cx, cy = x + w // 2, y + h // 2
        if 0 <= cy < design_mask.shape[0] and 0 <= cx < design_mask.shape[1] and design_mask[cy, cx] == 0:
            boxes.append({"text": text, "x": x, "y": y, "w": w, "h": h, "conf": conf})
    out = pil_img.copy()
    draw = ImageDraw.Draw(out)
    font = get_chinese_font(15)
    translated_count = 0
    translations = []
    for b in boxes:
        trans = translator.translate(b["text"])
        if trans:
            draw.rectangle([b["x"]-1, b["y"]-1, b["x"]+b["w"]+2, b["y"]+b["h"]+2], fill="white")
            draw.text((b["x"], b["y"]), trans, fill="black", font=font)
            translated_count += 1
            translations.append({"original": b["text"], "translated": trans})
    if show_protected and design_bbox[2] > design_bbox[0]:
        draw.rectangle(design_bbox, outline="red", width=3)
        draw.text((design_bbox[0]+10, design_bbox[1]+10), "PROTECTED DESIGN PACK", fill="red", font=font)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    out.save(output_path, quality=95)
    return {
        "input": input_path,
        "output": output_path,
        "boxes_detected": len(boxes),
        "translated": translated_count,
        "protected_bbox": design_bbox,
        "translations": translations,
    }
