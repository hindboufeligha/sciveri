def chunk_pages(
    pages: list[dict],
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[dict]:
    """
    Splits th extracted PDF pages into overlapping text chunks.

    Limitation:
        - the current global `chunk_size` counts across all pages
        rather than restarting for each page.

    Args:
        pages: Extracted page dictionaries containing: source, page, and text fields.
        chunk_size: Target max chunk length in characters.
        overlap: Number of characters carried between adjacent chunks.

    Returns:
        list[dict]: a list of chunk dictionaries with text and provenance metadata:
        source, page, chunk_index, and text.

    Raises:
        ValueError: If chunk_size is not positive, or overlap is negative
                    or >= chunk_size
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smallet than chunk_size")

    chunks = []
    for page in pages:
        text = page["text"].strip()

        if not text:
            continue

        paragraphs = text.split("\n\n")
        current_chunk = ""

        def save_chunk(chunk_text: str, page) -> None:
            chunks.append(
                {
                    "source": page["source"],
                    "page": page["page"],
                    "chunk_index": len(chunks),
                    "text": chunk_text,
                }
            )

        for paragraph in paragraphs:
            paragraph = paragraph.strip()

            # empty paragraph
            if not paragraph:
                continue

            # split paragraphs that exceed the target size into overlapping pieces
            if len(paragraph) > chunk_size:
                if current_chunk:
                    save_chunk(current_chunk, page)

                    current_chunk = ""

                start = 0

                while start < len(paragraph):
                    end = min(
                        start + chunk_size, len(paragraph)
                    )  # prevents the slice from extending beyond the para
                    piece = paragraph[start:end]
                    save_chunk(piece, page)

                    # stop once we've covered the entire para
                    if end == len(paragraph):
                        break

                    start += chunk_size - overlap

                continue

            # paragraph doesn't exceed the target size
            candidate = (
                f"{current_chunk}\n\n{paragraph}" if current_chunk else paragraph
            )

            if len(candidate) <= chunk_size:
                current_chunk = candidate

            else:
                save_chunk(current_chunk, page)

                # keep only as much overlap as fits with the new para
                seperator = "\n\n"
                available_overlap = max(0, chunk_size - len(paragraph) - len(seperator))

                previous_text = (
                    current_chunk[-available_overlap:] if available_overlap else ""
                )

                current_chunk = (
                    f"{previous_text}{seperator}{paragraph}"
                    if previous_text
                    else paragraph
                )

        if current_chunk:
            save_chunk(current_chunk, page)

    return chunks
