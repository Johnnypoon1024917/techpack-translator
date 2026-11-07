# Tech Pack Translator

Translate text in garment tech pack images to Chinese.  
The design artwork (the part that gets printed on the garment) is left completely untouched.

## Why this exists

Tech packs go between the Hong Kong design office and factories in different countries.  
A lot of the notes are in English. Factories need Chinese.  
The design image itself cannot be changed.

## What it does

- Finds text outside the design artwork
- Translates it (glossary or Qwen)
- Puts the Chinese back in roughly the same place
- Copies the original design artwork pixels back at the end so nothing is modified there

## Run it

```bash
pip install -r requirements.txt
python -m app.web_demo          # browser UI
# or
python -c "from app.core import process_techpack; process_techpack('samples/sample.jpg', 'out.jpg')"
```

Docker:
```bash
docker compose up web
```

## Layout

- `app/core.py` – main pipeline
- `app/advanced.py` – deskew, inpainting, metrics, etc.
- `app/api.py` – FastAPI
- `app/web_demo.py` – Gradio
- `ALGORITHM.md` – longer write-up of the approach

## Notes

The design artwork region is detected with a simple right-side heuristic or a user mask.  
User mask is more reliable.

Qwen needs `DASHSCOPE_API_KEY`. Without it the code falls back to the glossary.

Protected region PSNR is infinite when the paste is done correctly (tested).
