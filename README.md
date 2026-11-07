# Tech Pack Translator

Translate text in garment tech pack images to Chinese.  
The design artwork stays pixel-identical.

## Diagrams

- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- Pipeline: [docs/pipeline.md](docs/pipeline.md)
- SVG pictures: [docs/architecture.svg](docs/architecture.svg), [docs/pipeline.svg](docs/pipeline.svg)

## Run

```bash
pip install -r requirements.txt
python -m app.web_demo
```

## Files

- `app/core.py` — main pipeline and filtering
- `app/advanced.py` — deskew, inpainting, metrics, helpers
- `app/api.py` — FastAPI
- `app/web_demo.py` — Gradio
- `ALGORITHM.md` — formulation, special cases, evaluation
- `ARCHITECTURE.md` — structure and diagram

Artwork region: user mask or right-side heuristic.  
Qwen: set `DASHSCOPE_API_KEY`, otherwise glossary only.  
Protected-region PSNR is infinite after the final paste.
