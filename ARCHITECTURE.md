# Structure

```
original image ─────────────────────────────────────┐
                                            │
working copy                                │
  ├─ optional deskew / upscale              │
  ├─ detect artwork region                  │
  ├─ OCR                                    │
  ├─ filter boxes                           │
  ├─ translate                              │
  └─ draw Chinese                           │
                                            │
                    paste original artwork pixels
                                            │
                    output image ◄───────────┘
```

The paste is the last step. It uses a copy of the original that received the same geometric transforms (if any), so the coordinates match.

Optional pieces (inpainting, table row grouping, super-resolution, PSNR) sit beside the main path and can be enabled independently.

See `ALGORITHM.md` for the filtering rules and special cases.
