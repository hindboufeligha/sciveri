import pytest

from sciveri.chunking import chunk_pages


def test_chunk_pages_preserves_metadata():
    pages = [
        {
            "source": "sample.pdf",
            "page": 1,
            "text": "First paragraph.\n\nSecond paragraph",
        }
    ]

    chunks = chunk_pages(pages=pages)

    assert len(chunks) >= 1
    assert chunks[0]["source"] == "sample.pdf"
    assert chunks[0]["page"] == 1
    assert chunks[0]["chunk_index"] == 0
    assert chunks[0]["text"]


def test_chunk_pages_skips_empty_pages():
    pages = [
        {"source": "sample.pdf", "page": 1, "text": "     "},
        {"source": "sample.pdf", "page": 2, "text": "Hello world!"},
    ]

    chunks = chunk_pages(pages=pages)

    assert len(chunks) >= 1
    assert chunks[0]["page"] == 2


def test_chunk_pages_splits_long_paragraphs():
    pages = [{"source": "sample.pdf", "page": 1, "text": "A" * 25}]

    chunks = chunk_pages(pages=pages, chunk_size=10, overlap=2)

    assert len(chunks) > 1
    assert all(chunk["text"] for chunk in chunks)


@pytest.mark.parametrize(
    ("chunk_size", "overlap"),
    [
        (0, 0),
        (-1, 0),
        (10, -1),
        (10, 10),
        (10, 11),
    ],
)
def test_chunk_pages_rejects_invalud_params(chunk_size, overlap):
    with pytest.raises(ValueError):
        chunk_pages([], chunk_size=chunk_size, overlap=overlap)


def test_chunk_pages_respects_max_chunk_size():
    pages = [
        {
            "source": "sample.pdf",
            "page": 1,
            "text": "12345678\n\nkjdbkjsb",
        }
    ]

    chunk_size = 10

    chunks = chunk_pages(pages=pages, chunk_size=10, overlap=2)

    assert len(chunks) > 1
    assert all(len(chunk["text"]) <= chunk_size for chunk in chunks)


def test_chunk_pages_doesnot_create_redundant_trailing_chunk():
    pages = [
        {
            "source": "sample.pdf",
            "page": 1,
            "text": "A" * 25,
        }
    ]

    chunks = chunk_pages(pages=pages, chunk_size=10, overlap=2)

    assert len(chunks) == 3
    assert all(chunk["text"] for chunk in chunks)


def test_chunk_pages_preserves_overlap():
    pages = [
        {
            "source": "sample.pdf",
            "page": 1,
            "text": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        }
    ]

    chunks = chunk_pages(pages=pages, chunk_size=10, overlap=3)

    print([chunk["text"] for chunk in chunks])
    assert len(chunks) == 4
    assert chunks[0]["text"] == "ABCDEFGHIJ"
    assert chunks[1]["text"].startswith("HIJ")
    assert chunks[2]["text"].startswith("OPQ")
    assert chunks[3]["text"].startswith("VWX")


def test_chunk_pages_preserves_page_metadata_and_indices():
    pages = [
        {
            "source": "sample.pdf",
            "page": 1,
            "text": "Hello world!",
        },
        {
            "source": "sample.pdf",
            "page": 2,
            "text": "Second page content here.",
        },
    ]

    chunks = chunk_pages(pages=pages, chunk_size=10, overlap=2)

    page_one_chunks = [chunk for chunk in chunks if chunk["page"] == 1]
    page_two_chunks = [chunk for chunk in chunks if chunk["page"] == 2]

    assert len(page_one_chunks) == 2
    assert len(page_two_chunks) == 3
    assert all(chunk["source"] == "sample.pdf" for chunk in page_one_chunks)
    assert all(chunk["source"] == "sample.pdf" for chunk in page_two_chunks)

    assert all(chunk["page"] == 1 for chunk in page_one_chunks)
    assert all(chunk["page"] == 2 for chunk in page_two_chunks)

    assert [chunk["chunk_index"] for chunk in chunks] == list(range(len(chunks)))
