# Approach

## Constraint

The design artwork must be pixel-identical in the output.  
Everything else can be translated.

In code this is enforced by copying the original pixels of that region back at the very end.

## Pipeline

1. Optionally deskew / upscale the image (working copy only).
2. Detect the design artwork region (user mask or right-side heuristic).
3. Run OCR on the rest of the image.
4. Drop boxes that are inside the artwork, too small, low confidence, already Chinese, or look like watermarks.
5. Translate the remaining text (glossary first, Qwen if available).
6. Draw the Chinese text.
7. Paste the original artwork pixels back.
8. (Optional) compute PSNR on the artwork region – should be infinite.

## Translation

- Small glossary of common terms (placement, quantity, colors, topstitch, etc.).
- Fuzzy match for small OCR differences.
- Qwen (`qwen-plus`) with a short apparel-specific prompt when an API key is present.
- If Qwen fails, fall back to the glossary.

## Things that are handled

- Text already in Chinese → skipped
- Very small text or low OCR confidence → flagged, not translated
- Watermark-like text → skipped
- Long translations → font size reduced so it fits the box
- Deskew → same rotation applied to the original so the final paste still lines up

## Things that are only sketched

- Full table structure recognition
- Proper vision-language model path (Qwen-VL)
- Learned detector for the design artwork
- Real embedding-based RAG

These have basic hooks in `advanced.py` but are not the main path.

## Metrics

PSNR inside the protected region is the one that matters.  
It is measured before any red outline is drawn.  
With the current paste logic it comes out as infinite.
