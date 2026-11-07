"""
Advanced capabilities for the Tech Pack Translator.
Practical implementations of previously documented extensions.
"""
import cv2
import numpy as np
from PIL import Image, ImageFilter
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

def deskew_and_detect_rotation(pil_img: Image.Image) -> Tuple[Image.Image, float]:
    img = np.array(pil_img.convert("L"))
    edges = cv2.Canny(img, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=100)
    if lines is None:
        return pil_img, 0.0
    angles = [(theta * 180 / np.pi) - 90 for rho, theta in lines[:, 0] if -45 < (theta * 180 / np.pi - 90) < 45]
    if not angles:
        return pil_img, 0.0
    median_angle = float(np.median(angles))
    if abs(median_angle) < 0.5:
        return pil_img, 0.0
    rotated = pil_img.rotate(-median_angle, expand=True, fillcolor="white")
    logger.info(f"Deskewed by {median_angle:.2f} degrees")
    return rotated, median_angle

def group_into_table_cells(boxes: List[Dict], row_tol: int = 15) -> List[List[Dict]]:
    if not boxes:
        return []
    sorted_boxes = sorted(boxes, key=lambda b: b["y"])
    rows, current = [], [sorted_boxes[0]]
    for b in sorted_boxes[1:]:
        if abs(b["y"] - current[0]["y"]) <= row_tol:
            current.append(b)
        else:
            rows.append(sorted(current, key=lambda x: x["x"]))
            current = [b]
    rows.append(sorted(current, key=lambda x: x["x"]))
    return rows

def inpaint_text_regions(pil_img: Image.Image, boxes: List[Dict]) -> Image.Image:
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    for b in boxes:
        cv2.rectangle(mask, (b["x"], b["y"]), (b["x"]+b["w"], b["y"]+b["h"]), 255, -1)
    if mask.max() == 0:
        return pil_img
    inpainted = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB))

def simple_super_resolution(pil_img: Image.Image, scale: float = 2.0) -> Image.Image:
    w, h = pil_img.size
    up = pil_img.resize((int(w*scale), int(h*scale)), Image.BICUBIC)
    return up.filter(ImageFilter.SHARPEN)

def protected_region_psnr(original: Image.Image, output: Image.Image, bbox: Tuple[int,int,int,int]) -> float:
    x1, y1, x2, y2 = bbox
    if x2 <= x1 or y2 <= y1:
        return float("inf")
    o = np.array(original.crop((x1,y1,x2,y2))).astype(np.float32)
    n = np.array(output.crop((x1,y1,x2,y2))).astype(np.float32)
    mse = np.mean((o - n)**2)
    return float("inf") if mse == 0 else 20 * np.log10(255.0 / np.sqrt(mse))

class SimpleRAG:
    def __init__(self):
        self.memory = []
    def add(self, english: str, chinese: str):
        self.memory.append((english.lower().strip(), chinese))
    def retrieve(self, query: str, top_k: int = 3):
        q = set(query.lower().split())
        scored = [(len(q & set(e.split())), c) for e, c in self.memory if len(q & set(e.split())) > 0]
        scored.sort(reverse=True)
        return [c for _, c in scored[:top_k]]
