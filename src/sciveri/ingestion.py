from pathlib import Path

import pymupdf


def extract_pages(pdf_path: str) -> list[dict]:
    """Extracts text from each page of a PDF"""

    pages = []

    with pymupdf.open(pdf_path) as document:
        for page_no, page in enumerate(document, start=1):
            pages.append(
                {
                    "source": Path(pdf_path).name,
                    "page": page_no,
                    "text": page.get_text(),
                }
            )  # needed later for citations and evaluation (to not lose provenance)

    return pages
