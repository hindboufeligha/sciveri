from pathlib import Path

from sciveri.ingestion import extract_pages


def test_extract_pages():
    pdf_path = Path("tests/fixtures/sample.pdf")

    pages = extract_pages(str(pdf_path))

    assert len(pages) == 2
    assert pages[0]["page"] == 1
    assert pages[1]["page"] == 2
    assert pages[0]["source"] == "sample.pdf"
    assert "SciVeri" in pages[0]["text"]