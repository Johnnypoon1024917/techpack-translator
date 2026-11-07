# PhD-Grade Algorithm Design
## Tech Pack Image Translation with Hard Pixel-Preservation Constraint
### Crystal Group – AI Scientist Interview

---

## 1. Formal Problem Statement

Let \( I \in \mathbb{R}^{H \times W \times 3} \) be the input tech pack image.  
Let \( R_{design} \subset \{1\ldots H\} \times \{1\ldots W\} \) be the Design Pack Image region that must appear unchanged on the garment.

We seek a mapping \( f: I \mapsto I' \) such that:

1. **Semantic fidelity**: Necessary English text outside \( R_{design} \) is accurately rendered in Simplified Chinese.
2. **Hard pixel constraint**:
   \[
   I'(x,y) = I(x,y) \quad \forall (x,y) \in R_{design}
   \]
3. **Structural preservation**: Table geometry, callout lines, and technical drawings remain consistent.
4. **Terminology consistency**: Domain terms map to a stable Chinese lexicon \( \mathcal{L} \).

This is a constrained multi-modal generation problem under a strict equality constraint on a subset of pixels.

---

## 2. Modular Pipeline (Production Baseline)

### 2.1 Design Pack Region Estimation
- **User mask** (preferred): exact binary mask.
- **Learned detector**: fine-tuned DETR / YOLOv8-seg with Dice + box loss.
- **Heuristic fallback**: high-variance, low-text-density region (usually right side).

**Enforcement** (last step, non-negotiable):
```python
I_out[M == 1] = I_in[M == 1]
```

### 2.2 Text Detection & OCR
- Detector: DBNet++ / PaddleOCR DB.
- Recognizer: SVTR or CRNN (EN+ZH character set).
- Discard any box whose center lies inside \( R_{design} \) or confidence < 0.45.

### 2.3 Domain-Aware Translation (Cascade)
1. Glossary exact + fuzzy match (ratio ≥ 0.72).
2. **Qwen** (`qwen-plus` / `qwen-max`) with apparel-specific system prompt.
3. Optional RAG over past human-approved translations.

Lexicon enforcement: identical English terms always receive the same Chinese rendering.

### 2.4 Reconstruction
- **Overlay** (reliable): white-out box → adaptive-size Chinese text.
- **Inpainting** (advanced): LaMa / SD-inpaint then composite glyphs.

---

## 3. End-to-End Vision-Language Path

Qwen-VL / InternVL with structured prompt that returns design-pack bbox + translated spans.  
Hard pixel copy is still applied afterwards. Used as high-quality research track.

---

## 4. Special Cases & Exception Handling

| Special Case | Risk | Handling Strategy |
|--------------|------|-------------------|
| Design pack overlaps text | Accidental modification of artwork | User mask mandatory; detector trained on partial-overlap examples; any intersecting box is excluded |
| Handwritten annotations | OCR failure | Confidence gate; flag for human review; do not auto-translate |
| Already mixed EN/ZH | Double translation or corruption | Language detection per span; skip spans already in Chinese |
| Very small text (< 8 px) | Unreadable OCR | Upscale crop before OCR or flag for human |
| Rotated / vertical text | Missed by axis-aligned OCR | Use rotatable detector (e.g. PaddleOCR angle) or VLM path |
| Merged table cells | Broken structure | Table structure recognition (PaddleOCR Table / Table Transformer) before cell-level translation |
| Watermarks / stamps (“Page 1”, company logo) | Noise in OCR | Pre-filter by size + position; optional watermark removal |
| Multiple design images | Wrong region protected | Support multi-instance detection or multiple user masks |
| Callout arrows pointing into design pack | Arrow or label damaged | Exclude any box that intersects \( R_{design} \); preserve vector lines |
| Colored text on colored background | Poor contrast | Adaptive local contrast enhancement before OCR |
| Extremely long English phrases | Chinese overflow | Adaptive font sizing + optional controlled box expansion (still outside mask) |
| Low-resolution scan | Cascading OCR errors | Super-resolution (optional) + higher confidence threshold |
| Glossary conflict | Inconsistent terminology | Human-approved lexicon takes precedence; log conflicts |
| API failure (Qwen down) | Pipeline halt | Automatic fallback to glossary; retry with exponential back-off |

All exception paths either (a) fall back safely, (b) flag for human review, or (c) refuse to modify the protected region.

---

## 5. Evaluation Protocol

| Dimension | Metric | Target |
|-----------|--------|--------|
| Protected region integrity | PSNR / SSIM inside \( R_{design} \) | Exact (∞ / 1.0) |
| Translation quality | chrF++ / COMET on held-out sentences | ≥ human reference |
| Terminology consistency | Exact match vs gold lexicon | ≥ 98 % |
| Layout fidelity | Table cell IoU; Hausdorff distance of lines | IoU > 0.95 |
| End-to-end utility | Merchandiser correction time; factory error rate | Measured in pilot |

**Required ablations**: OCR vs VLM, glossary vs Qwen vs RAG, overlay vs inpainting, with vs without hard pixel copy.

---

## 6. Research Extensions

- Continual learning of the fashion glossary from human corrections
- Uncertainty estimation (self-consistency or LLM log-probs) to drive human review
- Synthetic data generation for design-pack detectors
- Cross-lingual layout adaptation when Chinese text length differs significantly
- Table-specific structure models

---

## 7. Interview One-Liner

“We formulate tech-pack translation as a constrained multi-modal generation problem whose primary invariant is pixel-level identity of the Design Pack Image; every module is swappable and every exception path is designed so that the invariant is never violated.”
