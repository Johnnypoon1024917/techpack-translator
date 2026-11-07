# Architecture – Tech Pack Translator

Designed for Crystal Group–style operations (Hong Kong HQ + global factories).

## System Diagram

```
                    ┌────────────────────┐
                    │   Input Tech Pack   │
                    │   (JPG/PNG/PDF)     │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Design Pack Mask   │◄── User mask (preferred)
                    │  Detection          │    or auto heuristic
                    └──────────┬──────────┘
                               │
              ┌───────────────┼───────────────┐
              │                │                │
     ┌───────▼────────┐      │       ┌────────▼────────┐
     │ Protected Region│      │       │ Text Regions    │
     │ (pixel copy)    │      │       │ OCR + bbox      │
     └────────┬────────┘      │       └────────┬────────┘
              │                │                │
              │         ┌──────▼──────┐         │
              │         │ Translator  │◄────────┘
              │         │ glossary /  │
              │         │ DeepL / LLM │
              │         └──────┬──────┘
              │                │
              └────────┬───────┘
                       │
              ┌────────▼────────┐
              │ Overlay Engine  │
              │ white-out + CN  │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │ Output Chinese  │
              │ Tech Pack Image │
              └──────────────────┘
```

## Key Design Decisions

1. **Protected region first**  
   Any pixel belonging to the Design Pack Image is never modified.  
   Production recommendation: always accept a user-drawn or pre-defined mask.

2. **Overlay instead of full re-layout**  
   Preserves technical drawings, callout lines, and table structure.

3. **Pluggable Translator**  
   `Translator` class supports glossary (offline), DeepL, and OpenAI.  
   Only one place to change for a new backend.

4. **API + UI**  
   FastAPI for system integration; Gradio for human review and interview demo.

5. **Observability**  
   Structured result dict + logging for audit (important in manufacturing).

## Production Roadmap

- PaddleOCR for higher table accuracy  
- Vision LLM (GPT-4o / Claude / Qwen-VL) for layout understanding  
- Glossary management UI for merchandisers  
- Batch processing queue (Celery / RQ)  
- Audit trail of every translation  
- Support for PDF multi-page tech packs  

## Crystal Group Context

Tech packs move between Hong Kong design teams and factories in China, Vietnam, Bangladesh, etc.  
Accurate Chinese translation of placement, color, quantity, and construction notes reduces errors and rework.  
The Design Pack Image (print/embroidery artwork) must remain untouched — this is non-negotiable.
