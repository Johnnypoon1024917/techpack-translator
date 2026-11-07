# Tech Pack Translator - Demo
# Translates garment tech pack images to Chinese while preserving the Design Pack Image

import cv2
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

# Simple domain glossary for demo (in production use LLM + glossary or DeepL)
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
    "CB": "后中",
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
}

def translate_text(text):
    text = text.strip()
    if text in GLOSSARY:
        return GLOSSARY[text]
    return f"[中] {text}"

def detect_design_pack_region(img):
    h, w = img.shape[:2]
    x1, y1, x2, y2 = 980, 10, 1480, 420
    mask = np.zeros((h, w), dtype=np.uint8)
    mask[y1:y2, x1:x2] = 255
    return mask, (x1, y1, x2, y2)

def process_techpack(input_path, output_path):
    pil_img = Image.open(input_path).convert("RGB")
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    design_mask, design_bbox = detect_design_pack_region(img)
    
    data = pytesseract.image_to_data(pil_img, lang='eng', output_type=pytesseract.Output.DICT)
    
    boxes = []
    for i in range(len(data['text'])):
        conf = int(data['conf'][i])
        text = data['text'][i].strip()
        if conf > 50 and text:
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            cx, cy = x + w//2, y + h//2
            if design_mask[cy, cx] == 0:
                boxes.append({'text': text, 'x': x, 'y': y, 'w': w, 'h': h, 'conf': conf})
    
    print(f"Processing {len(boxes)} text regions outside design pack...")
    
    output_img = pil_img.copy()
    draw = ImageDraw.Draw(output_img)
    
    font_paths = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    font = ImageFont.load_default()
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                font = ImageFont.truetype(fp, 14)
                break
            except:
                pass
    
    translated_count = 0
    for box in boxes:
        orig = box['text']
        trans = translate_text(orig)
        if not trans.startswith("[中]"):
            draw.rectangle([box['x'], box['y'], box['x']+box['w'], box['y']+box['h']], fill='white')
            draw.text((box['x'], box['y']), trans, fill='black', font=font)
            translated_count += 1
            print(f"  {orig[:40]:40} → {trans}")
    
    draw.rectangle(design_bbox, outline='red', width=3)
    draw.text((design_bbox[0]+10, design_bbox[1]+10), "PROTECTED DESIGN PACK", fill='red', font=font)
    
    output_img.save(output_path)
    print(f"\nDone! Translated {translated_count} texts. Output saved to {output_path}")
    print(f"Protected region: {design_bbox}")

if __name__ == "__main__":
    sample = os.path.join(os.path.dirname(__file__), "..", "samples", "sample_techpack.jpg")
    output = os.path.join(os.path.dirname(__file__), "..", "output_translated.jpg")
    process_techpack(sample, output)
