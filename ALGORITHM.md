# Algorithmic Formulation and Design
## Constrained Document Image Translation for Garment Tech Packs

### 1. Problem Definition

Let \( I \in \mathbb{R}^{H \times W \times 3} \) be the input image.  
Let \( R \subset \{1,\dots,H\} \times \{1,\dots,W\} \) be the pixel set of the design artwork.

We require
\[
I'(x,y) = I(x,y) \qquad \forall (x,y) \in R
\]
while textual content in the complement is replaced by Simplified Chinese.  
The equality is realized by an explicit pixel copy from a preserved (and identically transformed) original, performed after all other processing.

### 2. Baseline Cascade

Geometric normalization \( T \) (optional) → region estimate \( \hat{R} \) → OCR observations \( \mathcal{B}=\{(b_i,s_i,c_i)\} \) → filtering → translation cascade (lexicon then Qwen) → rendering → pixel copy of \( \hat{R} \) → PSNR verification.

A box is retained only when its center lies outside \( \hat{R} \), confidence and height pass thresholds, the string contains no CJK, and it is not watermark-like.

### 3. Special Cases — Mathematical Treatment and Importance

#### 3.1 Intersection with artwork
Center in \( \hat{R} \) (or nonempty intersection) → discard.  
Any write inside \( R \) can appear on the garment; this is the primary invariant.

#### 3.2 Pre-existing CJK
Unicode CJK range match → skip.  
Re-translation destroys correct content. Cost is linear in string length.

#### 3.3 Low confidence / handwriting
\( c_i < \tau \) or high recognition entropy → flag.  
Optional risk-based rule: translate only if \( \mathbb{E}[\ell(s_i,\hat s_i)\mid c_i]\le\epsilon \).  
Handwritten notes are common; an automatic error is more expensive than a human correction.

#### 3.4 Sub-resolution text
\( h(b_i)<h_{\min} \) → flag.  
Recognizer error rises sharply below a resolution limit.

#### 3.5 Watermarks
Excessive width or denylist match → suppress.  
These are not content and can overwrite nearby genuine text.

#### 3.6 Overflow
Binary search for largest font size whose rendered width fits the box.  
Prevents destruction of table alignment when a phrase expands.

#### 3.7 Translator failure
Deterministic lexicon fallback.  
Guarantees termination and never leaves a lexicon-covered string untranslated.

#### 3.8 Global skew
Single angle \( \theta \) estimated once; identical rotation applied to working image and preserved original.  
Independent estimation breaks the infinite-PSNR guarantee.

#### 3.9 Per-box rotation / vertical text
Global deskew removes page angle. Residual vertical text (aspect ratio \( h/w > 2.5 \)) is flagged.  
Full solution: estimate per-box \( \theta_i \) by maximizing horizontal projection variance after rotation, then recognize in the canonical frame.  
Call-outs are frequently rotated; missing them leaves English on the factory document.

#### 3.10 Table structure
Current: row clustering by \( y \)-coordinate.  
Full model: planar graph of cell boundaries; cell text = union of interior boxes.  
Merged cells are common in BOMs; a Table-Transformer stage can be inserted without touching the pixel copy.

#### 3.11 Multiple artwork regions
\( R=\bigcup_k R_k \). Accept a list of masks and protect the union.  
Packs often contain a main print plus a secondary label or embroidery; protecting only one region is insufficient.

#### 3.12 Low-contrast / coloured text
Local contrast below threshold → optional stretch or flag.  
Coloured headings and light-grey notes are otherwise missed or misread.

#### 3.13 Learned artwork detector
Minimize \( \lambda_{\mathrm{cls}}\mathcal{L}_{\mathrm{cls}}+\lambda_{\mathrm{box}}\mathcal{L}_{\mathrm{box}}+\lambda_{\mathrm{mask}}\mathcal{L}_{\mathrm{Dice}} \).  
Removes the right-side layout assumption. The final pixel copy is unchanged.

#### 3.14 End-to-end vision-language path
VLM returns proposed \( (b_j,s_j,t_j) \) and an artwork box; the same filter and pixel copy are applied afterwards.  
Reduces cascaded OCR error while the hard constraint remains enforced downstream.

#### 3.15 Retrieval-augmented lexicon
Embed phrases, retrieve top-\( k \) approved translations, supply as few-shot context.  
Improves consistency on phrases reused across seasons at negligible cost. Current code uses in-memory overlap.

### 4. Evaluation

Primary: PSNR on \( \hat{R} \) equals \( +\infty \).  
Secondary: chrF/COMET, lexicon exact-match, flag rate, cell IoU.  
Ablations should isolate each handler above.

### 5. Implementation

Sections 3.1–3.8, shared-transform logic, multi-region union, and vertical-text flagging are present in `app/core.py` / `app/advanced.py`.  
Remaining items have clear mathematical interfaces and can be substituted without relaxing \( I'|_R=I|_R \).
