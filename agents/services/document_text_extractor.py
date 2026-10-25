from __future__ import annotations

from io import BytesIO
from typing import ClassVar

import fitz
from docx import Document


class DocumentExtractionError(ValueError):
    """Raised when a document cannot be processed."""


class DocumentTextExtractor:
    SUPPORTED_EXTENSIONS: ClassVar[set[str]] = {".pdf", ".docx"}

    def extract(
        self,
        filename: str,
        content: bytes,
    ) -> str:
        extension = self._get_extension(filename)

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise DocumentExtractionError(
                "Unsupported file format. Only PDF and DOCX are supported."
            )

        if not content:
            raise DocumentExtractionError("Uploaded document is empty.")

        try:
            if extension == ".pdf":
                text = self._extract_pdf(content)
            else:
                text = self._extract_docx(content)
        except Exception as exc:
            raise DocumentExtractionError(
                "Unable to read the uploaded document."
            ) from exc

        normalized_text = text.strip()

        if not normalized_text:
            raise DocumentExtractionError("No extractable text found in the document.")

        return normalized_text

    @staticmethod
    def _get_extension(filename: str) -> str:
        from pathlib import Path

        return Path(filename).suffix.lower()

    @staticmethod
    def _extract_pdf(content: bytes) -> str:
        with fitz.open(
            stream=content,
            filetype="pdf",
        ) as document:
            pages = [page.get_text("text") for page in document]

        return "\n".join(pages)

    @staticmethod
    def _extract_docx(content: bytes) -> str:
        document = Document(BytesIO(content))

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n".join(paragraphs)
