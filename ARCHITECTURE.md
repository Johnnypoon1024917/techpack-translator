# Structure

Original image \( I \) is kept.  
A working copy is used for OCR and drawing.  

At the end the pixels of the artwork region \( R \) are copied from the (possibly transformed) original back into the output, enforcing

\[
I'(x,y) = I(x,y) \quad \forall (x,y) \in R
\]

Optional steps (deskew, upscale, inpainting, contrast) only touch the working copy.  
The same geometric transform is applied to the original so the paste stays aligned.

See `ALGORITHM.md` for the formal constraint, filtering rules, and which special cases are handled.
