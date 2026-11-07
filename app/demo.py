# Tech Pack Translator - Interview Solution
# Goal: Translate garment tech pack images to Chinese while keeping the Design Pack Image 100% unchanged.

import os
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw, ImageFont
from difflib import SequenceMatcher

# ---------------------------------------------------------------------------
# Domain glossary (expand this or replace with LLM / DeepL in production)
# ---------------------------------------------------------------------------
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

def fuzzy_translate(text, threshold=0.72):
    """Exact match first, then fuzzy match against glossary keys."""
    text = text.strip()
    if not text:
        return text
    if text in GLOSSARY:
        return GLOSSARY[text]
    best_ratio, best = 0, None
    for k, v in GLOSSARY.items():
        ratio = SequenceMatcher(None, text.lower(), k.lower()).ratio()
        if ratio > best_ratio:
            best_ratio, best = ratio, v
    if best_ratio >= threshold:
        return best
    return None


def detect_design_pack_region(img):
    """
    Heuristic for the sample: large graphic on the right side.
    Production options:
      - User-supplied mask
      - Object detection / segmentation
      - Low text-density + high color variance region
    """
    h, w = img.shape[:2]
    x1, y1 = int(w * 0.62), 5
    x2, y2 = w - 10, int(h * 0.52)
    mask = np.zeros((h, w), dtype=np.uint8)
    mask[y1:y2, x1:x2] = 255
    return mask, (x1, y1, x2, y2)


def get_chinese_font(size=16):
    candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def process_image(input_path, output_path, conf_threshold=45, show_protected=True):
    pil_img = Image.open(input_path).convert("RGB")
    img_cv = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    design_mask, design_bbox = detect_design_pack_region(img_cv)

    data = pytesseract.image_to_data(
        pil_img, lang="eng", output_type=pytesseract.Output.DICT
    )

    boxes = []
    for i in range(len(data["text"])):
        conf = float(data["conf"][i])
        text = data["text"][i].strip()
        if conf < conf_threshold or not text:
            continue
        x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
        cx, cy = x + w // 2, y + h // 2
        if design_mask[cy, cx] == 0:
            boxes.append({"text": text, "x": x, "y": y, "w": w, "h": h, "conf": conf})

    out = pil_img.copy()
    draw = ImageDraw.Draw(out)
    font = get_chinese_font(14)

    translated = 0
    for b in boxes:
        trans = fuzzy_translate(b["text"])
        if trans:
            draw.rectangle(
                [b["x"] - 1, b["y"] - 1, b["x"] + b["w"] + 1, b["y"] + b["h"] + 1],
                fill="white",
            )
            draw.text((b["x"], b["y"]), trans, fill="black", font=font)
            translated += 1

    if show_protected:
        draw.rectangle(design_bbox, outline="red", width=3)
        draw.text(
            (design_bbox[0] + 8, design_bbox[1] + 8),
            "PROTECTED",
            fill="red",
            font=font,
        )

    out.save(output_path)
    return {
        "boxes_processed": len(boxes),
        "translated": translated,
        "protected_bbox": design_bbox,
        "output": output_path,
    }


if __name__ == "__main__":
    sample = os.path.join(os.path.dirname(__file__), "..", "samples", "sample_techpack.jpg")
    output = os.path.join(os.path.dirname(__file__), "..", "output_translated.jpg")
    if os.path.exists(sample):
        result = process_image(sample, output)
        print(result)
    else:
        print(f"Sample not found: {sample}")
