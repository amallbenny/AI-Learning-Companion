import pymupdf as fitz

from modules.ocr import extract_text_with_ocr


def extract_text_from_pdf(pdf_path):

    text = ""

    pdf_document = fitz.open(pdf_path)

    for page_num in range(len(pdf_document)):

        page = pdf_document[page_num]

        text += page.get_text()

    pdf_document.close()

    print("Characters Extracted:", len(text))

    # Digital PDF
    if len(text.strip()) > 500:

        print("Using PyMuPDF Extraction")

        return text

    # Scanned PDF
    print("Using OCR Extraction")

    return extract_text_with_ocr(pdf_path)