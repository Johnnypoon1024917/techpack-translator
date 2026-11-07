# Comprehensive Algorithm Design
## Tech Pack Translation System (AI Scientist Level)

**Target**: Crystal Group – global apparel manufacturing  
**Role context**: AI Scientist (needs both rigorous method and production viability)

---

## 1. Problem Formulation

Given a tech pack image \( I \), produce a new image \( I' \) such that:

- All **necessary** English text is accurately translated into Simplified Chinese.
- The **Design Pack Image** region \( R_{design} \) is pixel-identical: \( I'(x,y) = I(x,y) \ \forall (x,y) \in R_{design} \).
- Technical drawings, callout lines, and table structure are preserved.
- Domain terminology (fit block, topstitch, YKK, fabric composition, etc.) is consistent.

This is a **constrained multi-modal document translation** problem with a hard pixel-preservation constraint.

---

## 2. Overall Architecture (Modular + Multi-modal Options)

Two complementary pipelines are supported:

| Pipeline | Strength | Best for |
|----------|----------|----------|
| **Modular (OCR → Translate → Overlay)** | Controllable, debuggable, high precision on protected region | Production baseline |
| **End-to-end Vision-Language** | Better layout understanding, fewer OCR errors | Research / high-quality path |

---

## 3. Detailed Components

### 3.1 Design Pack Image Detection (Critical Constraint)

**Approaches (in order of reliability)**:
1. **User-supplied mask** (recommended for production)
2. **Heuristic**: large high-variance, low-text-density region
3. **Learned detector**: fine-tuned YOLO / DETR or segmentation
4. **VLM prompting**: “Locate the design artwork that will be printed on the garment”

**Hard constraint**:
```python
output[mask > 0] = original[mask > 0]   # pixel-perfect copy
```

### 3.2 Translation Strategies

| Strategy | Method | Pros |
|----------|--------|------|
| Glossary + Fuzzy | Exact + SequenceMatcher | Fast, offline, consistent |
| **Qwen (text)** | DashScope with apparel system prompt | Strong Chinese, domain-tunable |
| **Qwen-VL** | Vision-language model | Sees layout + image context |
| RAG | Retrieve past translations + LLM | Improves consistency over time |

**Recommended path**: Glossary first → Qwen fallback → human review for low-confidence items.

### 3.3 Reconstruction

1. **Overlay mode** (current): white-out + redraw Chinese
2. **Inpainting mode** (advanced): LaMa / SD inpaint then render

### 3.4 Confidence & Human-in-the-Loop

- OCR + translation confidence
- Low-confidence items flagged for merchandiser review
- Approved translations added to glossary (active learning)

---

## 4. Evaluation Framework

| Metric | What it measures |
|--------|------------------|
| Translation quality | BLEU / chrF / COMET + human eval |
| Protected region integrity | PSNR / SSIM inside mask (must be perfect) |
| Layout preservation | Visual + table cell IoU |
| Terminology consistency | Glossary hit rate |
| End-to-end usability | Time-to-correct + factory error rate |

**Ablations to discuss**: OCR vs VLM, glossary vs Qwen vs RAG, overlay vs inpainting.

---

## 5. Research Directions

1. Multi-modal document understanding with Qwen-VL / InternVL
2. Table-specific models for structured tech packs
3. Continual learning of fashion glossary from human corrections
4. Uncertainty-aware translation
5. Cross-lingual layout transfer when text length differs
6. Synthetic data for better design-pack detectors

---

## 6. Interview Talking Points

- “We treat the Design Pack Image as a hard constraint, not a soft preference.”
- “Modular design lets us swap OCR for a VLM without rewriting the rest.”
- “Qwen is chosen because Chinese quality and cost are critical for our factories.”
- “We measure success by both translation accuracy and zero pixel change in the protected region.”
- “Human-in-the-loop + glossary update creates a data flywheel.”

This design is both **production-viable today** and **research-extensible** for an AI Scientist role.
