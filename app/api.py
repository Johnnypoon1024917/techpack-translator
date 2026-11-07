"""
FastAPI production endpoint
Run: uvicorn app.api:app --host 0.0.0.0 --port 8000
"""
import tempfile
import shutil
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from app.core import process_techpack, Translator

app = FastAPI(
    title="Tech Pack Translator API",
    description="Translate garment tech pack images to Chinese while preserving Design Pack Image. Built for Crystal Group–style operations.",
    version="1.0.0",
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "techpack-translator"}

@app.post("/translate")
async def translate(
    file: UploadFile = File(...),
    mask: UploadFile = File(None),
    backend: str = Form("glossary"),
    show_protected: bool = Form(True),
):
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        input_path = tmp_path / "input.jpg"
        output_path = tmp_path / "output.jpg"
        mask_path = None

        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        if mask:
            mask_path = tmp_path / "mask.png"
            with open(mask_path, "wb") as f:
                shutil.copyfileobj(mask.file, f)

        translator = Translator(backend=backend)
        result = process_techpack(
            str(input_path),
            str(output_path),
            mask_path=str(mask_path) if mask_path else None,
            translator=translator,
            show_protected=show_protected,
        )

        return FileResponse(
            output_path,
            media_type="image/jpeg",
            filename="translated_techpack.jpg",
            headers={"X-Translated-Count": str(result["translated"])},
        )

@app.post("/translate/json")
async def translate_json(
    file: UploadFile = File(...),
    backend: str = Form("glossary"),
):
    with tempfile.TemporaryDirectory() as tmp:
        input_path = Path(tmp) / "input.jpg"
        output_path = Path(tmp) / "output.jpg"
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        translator = Translator(backend=backend)
        result = process_techpack(str(input_path), str(output_path), translator=translator)
        return JSONResponse(result)
