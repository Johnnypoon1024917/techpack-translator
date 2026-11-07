# Tech Pack Translator

Translate text in garment tech pack images to Chinese.  
The design artwork stays pixel-identical.

## Run

```bash
pip install -r requirements.txt
python -m app.web_demo
```

Or:

```python
from app.core import process_techpack
process_techpack("samples/sample_techpack.jpg", "out.jpg")
```

## Files

- `app/core.py` — main pipeline and filtering
- `app/advanced.py` — deskew, inpainting, metrics, helpers
- `app/api.py` — FastAPI
- `app/web_demo.py` — Gradio
- `ALGORITHM.md` — how it works and what is handled
- `ARCHITECTURE.md` — short diagram

## Notes

Artwork region: user mask or right-side heuristic. Mask is better.  
Qwen: set `DASHSCOPE_API_KEY`, otherwise glossary only.  
Protected-region PSNR is infinite after the final paste (tested with and without deskew).
