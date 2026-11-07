# Qwen Backend (Recommended for Chinese)

Qwen (通义千问) is excellent for garment-industry Chinese translation.

### Setup
```bash
pip install dashscope
export DASHSCOPE_API_KEY=your_key_here
```

### Usage
```python
from app.core import Translator, process_techpack

translator = Translator(backend="qwen")
result = process_techpack("input.jpg", "output.jpg", translator=translator)
```

Or via API:
```bash
curl -X POST http://localhost:8000/translate \
  -F "file=@sample.jpg" \
  -F "backend=qwen"
```

The system prompt is tuned for apparel terminology (明线, 版型, YKK, etc.).
