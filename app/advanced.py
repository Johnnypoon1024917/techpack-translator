def apply_rotation(pil_img, angle):
    """Apply an exact rotation so two images stay pixel-aligned."""
    if abs(angle) < 0.1:
        return pil_img
    from PIL import Image
    return pil_img.rotate(-angle, expand=True, fillcolor="white", resample=Image.BICUBIC)

def deskew_and_detect_rotation(pil_img):
    import cv2, numpy as np
    from PIL import Image
    img = np.array(pil_img.convert("L"))
    edges = cv2.Canny(img, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi/180, 100)
    if lines is None:
        return pil_img, 0.0
    angles = [(theta*180/np.pi)-90 for rho, theta in lines[:,0] if -45 < (theta*180/np.pi-90) < 45]
    if not angles:
        return pil_img, 0.0
    median_angle = float(np.median(angles))
    if abs(median_angle) < 0.5:
        return pil_img, 0.0
    return apply_rotation(pil_img, median_angle), median_angle
