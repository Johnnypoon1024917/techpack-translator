# Approach

## The constraint that matters

The design artwork (the image that will be printed or embroidered on the garment) must be pixel-identical in the output.  
Everything else — tables, notes, callouts — can be translated to Chinese.

In the code this is enforced at the end: the original pixels of that region are copied back over whatever was drawn.  
PSNR inside the region is infinite when this is done correctly.

## Pipeline

1. Load the image. Keep an untouched copy.
2. Optional: deskew or upscale a working copy. The same geometric transform is applied to the untouched copy so coordinates still match later.
3. Find the design artwork region (user-supplied mask, or a simple right-side heuristic).
4. Run OCR on the working image. Throw away any box whose center is inside the artwork region, or that is too small, low-confidence, already Chinese, or looks like a watermark.
5. Translate the remaining text. Glossary first; Qwen if an API key is present. Fall back to glossary on failure.
6. Draw the Chinese text (font size reduced if it would overflow the box).
7. Paste the original artwork pixels back.
8. Optionally compute PSNR on the artwork region (measured before any red outline is drawn).

## Translation details

- Small fixed glossary for common terms (placement, quantity, colors, topstitch types, etc.).
- Fuzzy match so minor OCR differences still hit.
- Qwen (`qwen-plus`) with a short prompt that fixes a few apparel terms (topstitch → 明线, fit block → 版型, leave YKK codes alone).
- If the same English phrase appears more than once, the same Chinese is reused.

## Special cases

| Case | What the code does |
|------|--------------------|
| Box overlaps the design artwork | Dropped |
| Already contains Chinese | Skipped |
| Height < 8 px or low OCR confidence | Flagged, not translated |
| Looks like a page number or watermark | Skipped |
| Translation longer than the box | Font size reduced |
| Qwen call fails or no key | Glossary fallback |
| Deskew enabled | Same rotation applied to both copies so the final paste lines up |

Flagged items are returned in the result dict so a person can review them.

## What is only partially done

- Table structure (rows are grouped by y-coordinate; no full cell model yet)
- Vision-language path (interface exists, no live Qwen-VL call)
- Learned detector for the artwork region
- Proper embedding RAG (simple in-memory overlap for now)
- Inpainting (OpenCV Telea is available as an option)

These live in `advanced.py` and can be turned on with flags, but the default path does not depend on them.

## Metrics that matter

- PSNR / exact pixel match inside the artwork region (must be perfect)
- Whether domain terms stay consistent
- How many items get flagged for a human

chrF or COMET can be added later on a held-out set of sentences; they are not in the current code.
