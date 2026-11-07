# Approach

## Problem

Let \( I \) be the input image.  
Let \( R \) be the set of pixels that belong to the design artwork (the part printed on the garment).

We want an output image \( I' \) such that:

\[
I'(x,y) = I(x,y) \quad \forall (x,y) \in R
\]

and all relevant text outside \( R \) is replaced by its Chinese translation.

The equality is enforced by copying those pixels from the original at the end of the pipeline.  
When the copy is correct, PSNR inside \( R \) is infinite.

## Pipeline

1. Keep an untouched copy of \( I \).
2. Optional geometric transforms (deskew, upscale) are applied to a working copy.  
   The same transform is applied to the untouched copy so the coordinates of \( R \) still match.
3. Obtain \( R \) (user mask or right-side heuristic).
4. OCR → set of boxes \( \{(b_i, s_i, c_i)\} \).
5. Discard any box where the center lies in \( R \), or \( c_i \) is low, or the box is too small, or \( s_i \) already contains Chinese, or it looks like a watermark.
6. Translate the rest.
7. Draw Chinese text.
8. Copy original pixels of \( R \) back into the output.
9. (Optional) compute PSNR on \( R \) before any debug overlay is drawn.

## Translation

Glossary lookup (exact then fuzzy) followed by Qwen when a key is present.  
On failure, glossary is used.  
Repeated English strings reuse the same Chinese string.

## Special cases

| Case | Status | What happens |
|------|--------|--------------|
| Box center inside artwork | Handled | Box dropped |
| Already Chinese | Handled | Skipped |
| Very small text (< 8 px) | Handled | Flagged, not translated |
| Low OCR confidence | Handled | Flagged, not translated |
| Watermark / page number style | Handled | Skipped |
| Translation overflows box | Handled | Font size reduced |
| Qwen failure / no key | Handled | Glossary fallback |
| Deskew | Handled | Identical rotation on both copies; PSNR stays infinite |
| Colored text, low contrast | Partial | Optional contrast boost exists; not automatic |
| Rotated or vertical text | Partial | Global deskew only; per-box rotation not implemented |
| Merged table cells | Partial | Boxes grouped into rows by y; no real cell model |
| Multiple artwork regions | Partial | Single mask / single heuristic region |
| Handwriting | Partial | Caught by low-confidence flag; no special recognizer |
| Callout arrows crossing into artwork | Handled | Any box whose center is in \( R \) is dropped; lines themselves are not redrawn |
| Learned artwork detector | Not done | Heuristic or user mask only |
| Full vision-language path | Not done | Stub only |
| Embedding RAG | Not done | Simple in-memory overlap only |

Flagged items are returned so a person can check them.  
Nothing whose center lies in \( R \) is ever modified.

## Metrics

- PSNR inside \( R \) (target: infinite)
- Number of flagged items
- Consistency of repeated terms

Proper chrF / COMET would need a labeled set; not present yet.
