# Tech Pack Image Translator

**Production-ready interview solution for Crystal Group Hong Kong**

Translate garment tech pack images to Chinese while keeping the **Design Pack Image** 100% pixel-identical (it will be printed on the garment).

Factories are global; clients and colleagues are international. This system solves the daily communication problem.

---

## Challenges (面试要点)

| Challenge | Impact | Solution in this project |
|-----------|--------|--------------------------|
| Design Pack Image must stay unchanged | Printed on garment | User mask or auto heuristic + pixel copy |
| Position of design image varies | Different tech packs | Configurable mask or right-side heuristic |
| Mixed content (tables + drawings + callouts) | One model is not enough | OCR with bounding boxes + selective overlay |
| Text length changes (EN→ZH) | Layout breaks | Overlay inside original boxes |
| Domain terminology | Generic MT is poor | Fashion glossary + pluggable DeepL/LLM |
| Scan quality / watermarks | OCR errors | Confidence filter + preprocessing ready |

## Algorithm

1. Load image  
2. Detect / apply Design Pack mask (user mask preferred)  
3. OCR non-masked regions with bounding boxes  
4. Translate (glossary / DeepL / OpenAI)  
5. White-out original text → draw Chinese  
6. Optionally outline protected region for review  
7. Output final image  

See `ARCHITECTURE.md` for full design.

## Quick Start

### Web Demo (best for interview)
```bash
pip install -r requirements.txt
python -m app.web_demo
# http://localhost:7860
```

### API
```bash
uvicorn app.api:app --reload
# POST /translate  (returns image)
# POST /translate/json  (returns metadata)
```

### Docker
```bash
docker compose up web     # Gradio on :7860
docker compose up api     # FastAPI on :8000
```

## Project Structure
```
app/
  core.py          # Pipeline + Translator + mask logic
  api.py           # FastAPI production endpoint
  web_demo.py      # Gradio UI
Dockerfile
docker-compose.yml
requirements.txt
ARCHITECTURE.md
```

## Production Features

- **User-supplied mask** for exact Design Pack protection  
- **Pluggable translation** (`glossary` / `deepl` / `openai`)  
- **FastAPI** + **Gradio**  
- **Docker Compose**  
- Structured logging & JSON results  
- Easy to swap Tesseract → PaddleOCR  

## For Crystal Group Interview

This demonstrates:
- Understanding of global apparel manufacturing pain points  
- Careful handling of print-critical graphics  
- Clean, extensible architecture  
- Ready-to-demo web UI and API  

Add your real DeepL / Azure / OpenAI key and the system becomes fully production-ready.
