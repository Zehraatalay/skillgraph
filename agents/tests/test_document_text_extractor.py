from io import BytesIO

import fitz
import pytest
from docx import Document

from agents.services.document_text_extractor import (
    DocumentExtractionError,
    DocumentTextExtractor,
)


@pytest.fixture
def extractor():
    return DocumentTextExtractor()


def create_pdf(text: str) -> bytes:
    document = fitz.open()

    page = document.new_page()
    page.insert_text((72, 72), text)

    content = document.tobytes()
    document.close()

    return content


def create_docx(text: str) -> bytes:
    document = Document()
    document.add_paragraph(text)

    buffer = BytesIO()
    document.save(buffer)

    return buffer.getvalue()


def test_extract_pdf(extractor):
    content = create_pdf("Python Machine Learning")

    result = extractor.extract(
        filename="resume.pdf",
        content=content,
    )

    assert "Python Machine Learning" in result


def test_extract_docx(extractor):
    content = create_docx("Python Data Science")

    result = extractor.extract(
        filename="resume.docx",
        content=content,
    )

    assert "Python Data Science" in result


def test_reject_unsupported_extension(extractor):
    with pytest.raises(
        DocumentExtractionError,
        match="Unsupported file format",
    ):
        extractor.extract(
            filename="resume.txt",
            content=b"Python",
        )


def test_reject_empty_file(extractor):
    with pytest.raises(
        DocumentExtractionError,
        match="Uploaded document is empty",
    ):
        extractor.extract(
            filename="resume.pdf",
            content=b"",
        )


def test_reject_invalid_pdf(extractor):
    with pytest.raises(
        DocumentExtractionError,
        match="Unable to read",
    ):
        extractor.extract(
            filename="resume.pdf",
            content=b"not a real pdf",
        )


def test_reject_pdf_without_text(extractor):
    document = fitz.open()
    document.new_page()

    content = document.tobytes()
    document.close()

    with pytest.raises(
        DocumentExtractionError,
        match="No extractable text",
    ):
        extractor.extract(
            filename="resume.pdf",
            content=content,
        )
