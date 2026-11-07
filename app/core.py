"""
Production-oriented Tech Pack Translator with special-case handling.
Designed for Crystal Group–style global apparel operations.

Special cases handled:
- Design pack overlap → exclude intersecting boxes
- Low confidence / handwriting → flag, do not auto-translate
- Already Chinese → skip
- Very small text → skip or flag
- Watermarks / stamps → size + position filter
- Long text overflow → adaptive font size
- Qwen API failure → automatic glossary fallback
- Colored / low-contrast text → optional contrast boost
"""

import os
import re
import logging
from typing import Optional, Tuple, Dict, Any, List
from pathlib import Path

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from difflib import SequenceMatcher

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

GLOSSARY = {
    "Style Name:": "款式名称:",
    "Placement": "位置",
    "Quantity": "数量",
    "Yards": "码",
    "Beige": "米色",
    "Black": "黑色",
    "White": "白色",
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

CHINESE_RE = re.compile(r"[\u4e00-\u9fff]")

def contains_chinese(text: str) -> bool:
    return bool(CHINESE_RE.search(text))

class Translator:
    def __init__(self, backend: str = "glossary", api_key: Optional[str] = None):
        self.backend = backend.lower()
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY") or os.getenv("TRANSLATION_API_KEY")

    def translate(self, text: str) -> Optional[str]:
        text = text.strip()
        if not text or contains_chinese(text):
            return None
        if self.backend == "qwen":
            return self._qwen(text)
        return self._glossary(text)

    def _glossary(self, text: str, threshold: float = 0.70) -> Optional[str]:
        if text in GLOSSARY:
            return GLOSSARY[text]
        best_ratio, best = 0.0, None
        for k, v in GLOSSARY.items():
            ratio = SequenceMatcher(None, text.lower(), k.lower()).ratio()
            if ratio > best_ratio:
                best_ratio, best = ratio, v
        return best if best_ratio >= threshold else None

    def _qwen(self, text: str) -> Optional[str]:
        if not self.api_key:
            return self._glossary(text)
        try:
            import dashscope
            from dashscope import Generation
            dashscope.api_key = self.api_key
            system_prompt = (
                "You are a professional apparel technical translator. "
                "Translate the English tech-pack phrase into concise Simplified Chinese. "
                "Keep terms consistent (topstitch=明线, fit block=版型, YKK unchanged). "
                "Output ONLY the Chinese translation."
            )
            resp = Generation.call(
                model="qwen-plus",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                result_format="message",
            )
            if resp.status_code == 200:
                return resp.output.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Qwen failed ({e}) → glossary fallback")
        return self._glossary(text)

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

def adaptive_font_size(draw, text, max_width, max_height, base_size=16):
    low, high = 8, base_size
    best = 8
    while low <= high:
        mid = (low + high) // 2
        font = get_chinese_font(mid)
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if tw <= max_width and th <= max_height:
            best = mid
            low = mid + 1
        else:
            high = mid - 1
    return get_chinese_font(best)

def process_techpack(
    input_path: str,
    output_path: str,
    mask_path: Optional[str] = None,
    translator: Optional[Translator] = None,
    conf_threshold: float = 45.0,
    min_text_height: int = 8,
    show_protected: bool = True,
    enhance_contrast: bool = False,
) -> Dict[str, Any]:
    if translator is None:
        translator = Translator(backend="glossary")

    pil_img = Image.open(input_path).convert("RGB")
    if enhance_contrast:
        pil_img = ImageEnhance.Contrast(pil_img).enhance(1.4)

    img_cv = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    design_mask, design_bbox = detect_design_pack_region(img_cv, mask_path)
    h, w = design_mask.shape

    data = pytesseract.image_to_data(pil_img, lang="eng", output_type=pytesseract.Output.DICT)

    boxes = []
    flagged = []

    for i in range(len(data["text"])):
        try:
            conf = float(data["conf"][i])
        except (ValueError, TypeError):
            continue
        text = data["text"][i].strip()
        if not text:
            continue

        x, y, bw, bh = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
        cx, cy = x + bw // 2, y + bh // 2

        if not (0 <= cy < h and 0 <= cx < w):
            continue
        if design_mask[cy, cx] > 0:
            continue
        if bh < min_text_height:
            flagged.append({"text": text, "reason": "too_small", "conf": conf})
            continue
        if conf < conf_threshold:
            flagged.append({"text": text, "reason": "low_confidence", "conf": conf})
            continue
        if bw > w * 0.6 or text.lower() in {"page", "page 1", "confidential"}:
            flagged.append({"text": text, "reason": "watermark_like", "conf": conf})
            continue
        if contains_chinese(text):
            continue

        boxes.append({"text": text, "x": x, "y": y, "w": bw, "h": bh, "conf": conf})

    out = pil_img.copy()
    draw = ImageDraw.Draw(out)

    translated_count = 0
    translations = []
    for b in boxes:
        trans = translator.translate(b["text"])
        if not trans:
            flagged.append({"text": b["text"], "reason": "no_translation", "conf": b["conf"]})
            continue

        font = adaptive_font_size(draw, trans, b["w"] + 4, b["h"] + 2, base_size=16)
        draw.rectangle(
            [b["x"] - 1, b["y"] - 1, b["x"] + b["w"] + 2, b["y"] + b["h"] + 2],
            fill="white",
        )
        draw.text((b["x"], b["y"]), trans, fill="black", font=font)
        translated_count += 1
        translations.append({"original": b["text"], "translated": trans})

    # Hard pixel-perfect copy of protected region (safety net)
    if design_bbox[2] > design_bbox[0]:
        x1, y1, x2, y2 = design_bbox
        region = pil_img.crop((x1, y1, x2, y2))
        out.paste(region, (x1, y1))
        if show_protected:
            draw = ImageDraw.Draw(out)
            draw.rectangle(design_bbox, outline="red", width=3)
            font_small = get_chinese_font(12)
            draw.text((x1 + 8, y1 + 8), "PROTECTED", fill="red", font=font_small)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    out.save(output_path, quality=95)

    result = {
        "backend": translator.backend,
        "boxes_considered": len(boxes) + len(flagged),
        "translated": translated_count,
        "flagged": flagged,
        "protected_bbox": design_bbox,
        "translations": translations,
    }
    logger.info(f"Done: translated={translated_count}, flagged={len(flagged)}")
    return result
