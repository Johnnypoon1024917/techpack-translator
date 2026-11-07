# Algorithmic Formulation and Design
## Constrained Document Image Translation for Garment Tech Packs

### 1. Problem Definition

Let \( I \in \mathbb{R}^{H \times W \times 3} \) denote the input tech-pack image.  
Let \( R \subset \{1,\dots,H\} \times \{1,\dots,W\} \) be the (latent) pixel set corresponding to the design artwork that will be physically realized on the garment.

The objective is to produce \( I' \) satisfying the hard constraint

\[
I'(x,y) = I(x,y) \qquad \forall (x,y) \in R
\]

while replacing textual content in \( \Omega = \{1,\dots,H\} \times \{1,\dots,W\} \setminus R \) by its Simplified-Chinese translation.  
Secondary objectives are preservation of geometric structure (table rulings, call-out leaders) and terminological consistency with respect to a domain lexicon \( \mathcal{L} \).

This is an instance of constrained multi-modal generation under an equality constraint on a subset of the output support.

### 2. Overall Procedure

The implemented system follows a modular cascade.  
Each stage is deliberately replaceable.

1. **Geometric normalization** (optional).  
   A working copy \( I_w \) is obtained by a similarity transform \( T \) (deskew and/or isotropic up-sampling).  
   The identical transform is applied to a preserved copy \( I_0 \) so that coordinates remain commensurate.

2. **Artwork region estimation**.  
   \( \hat{R} \) is obtained either from a user-supplied binary mask or from a lightweight heuristic (high-variance, low text-density region, typically the right-hand portion of the page).  
   A learned detector is a straightforward extension but is not required for the baseline.

3. **Text detection and recognition**.  
   An off-the-shelf detector-recognizer yields a set of observations
   \[
   \mathcal{B} = \{(b_i, s_i, c_i)\}_{i=1}^N
   \]
   where \( b_i \) is a bounding box, \( s_i \) the recognized string and \( c_i \in [0,1] \) a confidence.

4. **Filtering**.  
   A box is retained only if its center lies outside \( \hat{R} \), confidence exceeds a threshold, height is sufficient, the string contains no CJK characters, and it is not watermark-like.  
   Rejected boxes are recorded for human review.

5. **Translation**.  
   Cascade: lexicon (exact then fuzzy) → Qwen-Plus with apparel prompt → lexicon on failure.  
   Identical source strings map to identical target strings.

6. **Rendering**.  
   Chinese text is placed inside each retained box; font size is selected by binary search to respect box bounds.

7. **Constraint enforcement**.  
   Pixels of \( \hat{R} \) are copied from the transformed preserved original.  
   This step is independent of earlier modules.

8. **Verification**.  
   PSNR on \( \hat{R} \) is computed before any diagnostic overlay.  
   Correct implementation yields \( +\infty \).

### 3. Design Rationale

The hard constraint is realized by an explicit copy rather than a soft penalty, guaranteeing the invariant even under upstream failure.  
Modularity allows substitution of OCR, translator or inpainter without touching the constraint mechanism.  
Rejected boxes are returned, giving a lightweight human-in-the-loop.

### 4. Special Cases

| Phenomenon | Treatment | Completeness |
|------------|-----------|--------------|
| Intersection with artwork | Discard if center inside | Complete (axis-aligned) |
| Pre-existing CJK | Language filter | Complete |
| Low confidence / handwriting | Threshold + flag | Partial |
| Sub-resolution text | Height gate | Complete |
| Watermarks | Size/lexical filter | Heuristic |
| Overflow | Adaptive font size | Complete (single-line) |
| API failure | Lexicon fallback | Complete |
| Global skew | Shared transform | Complete |
| Per-box rotation / vertical | — | Open |
| Complex table structure | Row clustering only | Partial |
| Multiple artwork regions | Single-region assumption | Open |
| Low-contrast colour text | Optional stretch | Partial |
| Learned region predictor | — | Open |
| End-to-end VLM | Interface only | Open |
| Embedding retrieval | In-memory overlap | Rudimentary |

### 5. Evaluation

Primary: PSNR on the artwork region (target \( +\infty \)).  
Secondary (future): COMET/chrF on held-out sentences, lexicon exact-match rate, flag rate, geometric fidelity of rulings.  
Recommended ablations: OCR vs VLM front-end, lexicon vs LLM vs retrieval, overlay vs inpainting, presence vs absence of the final pixel copy.

### 6. Limitations and Extensions

The baseline favours an auditable cascade.  
Natural extensions (none of which relax the pixel constraint) include a learned segmenter for \( R \), a vision-language front-end still followed by the pixel copy, a vector store of approved translations, proper table-structure recognition, and uncertainty estimates to prioritize review.

### 7. Implementation

The cascade, shared-transform bookkeeping, filtering, adaptive rendering and PSNR check are implemented in `app/core.py` and `app/advanced.py`.  
Items marked Open or Partial have only interfaces or simplified surrogates.
