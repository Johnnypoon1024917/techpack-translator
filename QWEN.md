# Qwen

Uses DashScope (`qwen-plus`).

```bash
export DASHSCOPE_API_KEY=sk-...
```

```python
from app.core import Translator, process_techpack
t = Translator(backend="qwen")
process_techpack("in.jpg", "out.jpg", translator=t)
```

Falls back to the glossary if the key is missing or the call fails.
