# Structure

Working image goes through OCR and translation.  
Original design artwork pixels are pasted back at the end.

Optional steps (deskew, upscale, inpainting) only affect the working copy.  
The paste uses a copy that received the same geometric transforms so coordinates still match.

See `ALGORITHM.md` for the step-by-step.
