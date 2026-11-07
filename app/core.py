# See local app/core.py – key fixes applied:
# 1. Angle computed once, apply_rotation() used on both original and working image
# 2. PSNR calculated immediately after paste, before red outline is drawn
# Result: protected_psnr = inf even with deskew=True
