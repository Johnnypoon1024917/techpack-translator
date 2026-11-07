# Tech Pack Image Translator

**Interview solution** — Translate garment tech pack images to Chinese while keeping the **Design Pack Image** 100% pixel-identical (it will be printed on the garment).

## Challenges

| Challenge | Why it matters | Approach in this project |
|-----------|----------------|--------------------------|
| Protected Design Pack Image | Must appear exactly as designed on the garment; position varies | Heuristic region detection + mask; copy pixels unchanged |
| Mixed layout | Tables, callouts, technical drawings, logos | OCR with bounding boxes; process only text regions |
| Text length change | Chinese is usually shorter | Overlay inside original bounding boxes |
| Domain terms | Fit Block, YKK, topstitch, fabric compositions | Fashion glossary + fuzzy matching |
| OCR quality | Scans, watermarks, small text | Tesseract + confidence filter; easy to swap for PaddleOCR |
| Reconstruction | Must not destroy line drawings | White-out only text pixels then redraw Chinese |

## Algorithm (high-level)

1. Load image  
2. Detect / mask Design Pack Image region  
3. OCR remaining areas (bounding boxes + confidence)  
4. Fuzzy-match + glossary translation  
5. White-out original English text and overlay Chinese  
6. Optionally draw protected-region outline for review  
7. Save output image  

## Quick Start

### Local
```bash
pip install -r requirements.txt
# Place sample at samples/sample_techpack.jpg
python app/demo.py
# → output_translated.jpg
```

### Web UI (recommended for demo)
```bash
python app/web_demo.py
# Open http://localhost:7860
```

### Docker
```bash
docker build -t techpack-translator .
docker run -p 7860:7860 -v $(pwd):/app techpack-translator python app/web_demo.py
```

## Project Structure
```
app/
  demo.py          # Core pipeline (OCR + translate + overlay)
  web_demo.py      # Gradio UI
samples/           # Put sample_techpack.jpg here
Dockerfile
requirements.txt
ARCHITECTURE.md
```

## Production Upgrades (for higher score)
- Replace glossary with DeepL / Google Translate / GPT-4o + fashion glossary
- Switch to **PaddleOCR** for better table and Chinese support
- Accept user-supplied mask for the Design Pack Image
- Table structure recognition (PaddleOCR table)
- Multi-line text fitting and font-size adaptation
- Batch processing / API endpoint

## Notes
- The Design Pack Image region is currently tuned for the provided sample.  
  In production, use a user mask or a trained detector.
- Translation is glossary + fuzzy match so the demo runs offline.  
  Swap `fuzzy_translate()` for any API in one place.
