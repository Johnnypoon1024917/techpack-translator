# Architecture

Two images are maintained:

- \( I_0 \): preserved original (receives only the same global geometric transform \( T \) as the working copy);
- \( I_w \): working copy used for detection, recognition, translation and rendering.

After rendering, the constraint

\[
I'|_{\hat{R}} = (T(I_0))|_{\hat{R}}
\]

is realized by direct pixel copy.

```mermaid
flowchart TB
    subgraph Original["I_0 (Preserved Original)"]
        A1[Input Image] --> A2[Shared transform T]
        A2 --> A3[Preserved for final copy]
    end

    subgraph Working["I_w (Working Copy)"]
        B1[Input Image] --> B2[Optional deskew / upscale]
        B2 --> B3[Detect artwork region R-hat]
        B3 --> B4[OCR]
        B4 --> B5[Filter boxes]
        B5 --> B6[Translate lexicon / Qwen]
        B6 --> B7[Render Chinese]
    end

    A3 --> C[Pixel copy of R-hat<br/>I-prime on R-hat = T of I_0 on R-hat]
    B7 --> C
    C --> D[Output Image]
```

![Architecture](docs/architecture.svg)

Optional modules never write inside \( \hat{R} \) once the copy has been performed.

Full detail is in `ALGORITHM.md`. Pipeline: `docs/pipeline.md`.
