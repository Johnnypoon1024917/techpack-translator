"""
Gradio web demo – recommended for interview live demo
Run: python -m app.web_demo
"""
import tempfile
from pathlib import Path
import gradio as gr
from app.core import process_techpack, Translator

def translate_ui(image, show_protected):
    if image is None:
        return None, "Please upload a tech pack image."
    with tempfile.TemporaryDirectory() as tmp:
        in_path = Path(tmp) / "input.jpg"
        out_path = Path(tmp) / "output.jpg"
        image.save(in_path)
        translator = Translator(backend="glossary")
        info = process_techpack(
            str(in_path),
            str(out_path),
            translator=translator,
            show_protected=show_protected,
        )
        msg = (
            f"Detected {info['boxes_detected']} text regions. "
            f"Translated {info['translated']} terms. "
            f"Protected region: {info['protected_bbox']}"
        )
        return str(out_path), msg

with gr.Blocks(title="Tech Pack Translator | Crystal Group Style") as demo:
    gr.Markdown(
        """
        # Tech Pack Image Translator
        **Crystal Group–style solution**  
        Translate English tech pack text to Chinese while keeping the **Design Pack Image** 100% unchanged  
        (it will be printed on the garment).

        ### How to use
        1. Upload a tech pack image  
        2. Click **Translate**  
        3. Protected design pack is outlined in red and left pixel-perfect
        """
    )
    with gr.Row():
        inp = gr.Image(type="pil", label="Upload Tech Pack")
        out = gr.Image(label="Translated Result")
    show_box = gr.Checkbox(label="Show protected region outline", value=True)
    status = gr.Textbox(label="Status", interactive=False)
    btn = gr.Button("Translate to Chinese", variant="primary")
    btn.click(translate_ui, inputs=[inp, show_box], outputs=[out, status])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
