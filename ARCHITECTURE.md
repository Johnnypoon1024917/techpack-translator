# Architecture

Two images are maintained:

- \( I_0 \): preserved original (receives only the same global geometric transform \( T \) as the working copy);
- \( I_w \): working copy used for detection, recognition, translation and rendering.

After rendering, the constraint

\[
I'|_{\hat{R}} = (T(I_0))|_{\hat{R}}
\]

is realized by direct pixel copy.  
Diagnostic overlays occur only after the copy and after PSNR measurement.

Optional modules never write inside \( \hat{R} \) once the copy has been performed.

Full algorithmic detail, filtering predicates, special-case analysis and evaluation criteria are in `ALGORITHM.md`.
