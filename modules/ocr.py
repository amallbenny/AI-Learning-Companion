import os
import fitz  # PyMuPDF
from paddleocr import PaddleOCR
import numpy as np
from PIL import Image
import io

# initialize ONCE (important)
ocr = PaddleOCR(use_angle_cls=True, lang="en")


def extract_text_with_ocr(pdf_path):

    doc = fitz.open(pdf_path)
    full_text = []

    for page_index in range(len(doc)):

        page = doc.load_page(page_index)

        # convert page to image
        pix = page.get_pixmap()

        img_bytes = pix.tobytes("png")

        image = Image.open(io.BytesIO(img_bytes))

        image = np.array(image)

        # -----------------------------
        # SAFETY CHECK (IMPORTANT FIX)
        # -----------------------------
        if image is None or image.size == 0:
            continue

        try:
            result = ocr.ocr(image, cls=True)

            if result is None:
                continue

            for line in result[0]:
                full_text.append(line[1][0])

        except Exception as e:
            print(f"OCR failed on page {page_index}: {e}")
            continue

    return "\n".join(full_text)