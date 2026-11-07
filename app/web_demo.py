"""
Gradio web demo for the Tech Pack Translator.
Run: python app/web_demo.py
"""
import os
import tempfile
import gradio as gr
from demo import process_image

def translate_ui(image):
    if image is None:
        return None, "Please upload a tech pack image."
    with tempfile.TemporaryDirectory() as tmp:
        in_path = os.path.join(tmp, "input.jpg")
        out_path = os.path.join(tmp, "output.jpg")
        image.save(in_path)
        info = process_image(in_path, out_path, show_protected=True)
        return out_path, (
            f"Processed {info['boxes_processed']} text regions. "
            f"Translated {info['translated']} terms. "
            f"Protected region: {info['protected_bbox']}"
        )

with gr.Blocks(title="Tech Pack Translator") as demo:
    gr.Markdown(
        """
        # Tech Pack Image Translator (Garment Industry)
        Translate English text in tech pack images to Chinese  
        while **preserving the Design Pack Image** exactly (it will be printed on the garment).

        **How to use**
        1. Upload a tech pack image
        2. Click *Translate*
        3. The protected design pack region is marked in red and left unchanged
        """
    )
    with gr.Row():
        inp = gr.Image(type="pil", label="Upload Tech Pack")
        out = gr.Image(label="Translated Result")
    status = gr.Textbox(label="Status", interactive=False)
    btn = gr.Button("Translate to Chinese", variant="primary")
    btn.click(translate_ui, inputs=inp, outputs=[out, status])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
