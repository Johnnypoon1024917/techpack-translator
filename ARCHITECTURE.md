# Architecture

## System Overview

```
Input Image
    │
    ▼
Preprocessing (optional deskew / contrast)
    │
    ▼
Design Pack Region Detection  ──► Mask (pixel-perfect copy)
    │
    ▼
OCR (Tesseract / PaddleOCR) on non-masked areas
    │
    ▼
Filter by confidence
    │
    ▼
Domain-aware Translation (glossary + fuzzy / LLM / MT API)
    │
    ▼
Text Placement (white-out + draw Chinese)
    │
    ▼
Output Chinese Tech Pack Image
```

## Key Design Decisions

1. **Protected region first**  
   Any pixel inside the Design Pack Image is never modified.  
   Detection is currently a simple geometric heuristic; production should use a user mask or a small detector.

2. **OCR with bounding boxes**  
   We keep the original layout. Translation is overlaid, not a full re-layout.  
   This preserves technical drawings and callout lines.

3. **Pluggable translation**  
   `fuzzy_translate()` is the only place that needs to change to plug in DeepL, Google, Azure, or an LLM.

4. **Visualization**  
   Optional red outline around the protected region so reviewers can verify the Design Pack Image was untouched.

## Future Extensions

- PaddleOCR table recognition for structured cells  
- User-uploaded mask (PNG) for arbitrary Design Pack positions  
- LLM vision model for layout understanding + translation in one pass  
- Gradio / FastAPI production service  
- Glossary management UI for fashion terms
