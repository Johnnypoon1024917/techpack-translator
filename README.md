# Tech Pack Image Translator (Garment Industry)

Translate English text in garment tech pack images to Chinese while **preserving the Design Pack Image** exactly (it will be printed on the garment).

## Challenges Addressed
- Mixed layout (tables + technical drawings + graphics)
- Protected design pack region detection
- Domain-specific translation
- Layout preservation after translation (Chinese is more compact)

## Algorithm
1. Preprocess image
2. Detect & mask Design Pack Image region
3. OCR remaining regions (Tesseract / PaddleOCR)
4. Translate with glossary + MT API / LLM
5. White-out original text & overlay Chinese
6. Output new image

## Quick Test (local)
```bash
python3 app/demo.py
# Output: output_translated.jpg
```

## Docker
```bash
docker build -t techpack-translator .
docker run -v $(pwd):/app techpack-translator
```

## Production Improvements
- Replace glossary with DeepL / Google Translate / GPT-4o + fashion glossary
- Better table structure recognition (PaddleOCR table)
- User-supplied mask or automatic detection for Design Pack Image
- Gradio web UI for upload
- Handle multi-line text and font size fitting

## Sample
Place your tech pack image as `samples/sample_techpack.jpg` and run.
