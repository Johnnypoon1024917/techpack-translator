# Failure cases

## 1. Tight cell overflow
Chinese longer than the box may clip at minimum font size (8 px). System does not reflow into adjacent cells. Flag if final size equals minimum.

## 2. Artwork not on the right
Default heuristic assumes right-side artwork. If artwork is left or center, mask is wrong. Mitigation: user mask or detect_artwork_by_density (text-density + variance). Learned detector is the long-term fix.

## 3. Handwritten call-outs
Low-confidence OCR is flagged, not auto-translated. Correct, but review queue can be large.

## 4. Multi-line merged cells
Row clustering is by y only. Merged cells spanning rows are split. Protected region is still preserved.
