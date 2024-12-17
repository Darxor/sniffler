from pathlib import Path

import pymupdf

from .base import InfoValue


class PdfResearcher:
    """
    A class to perform research operations on PDF files.
    """

    @staticmethod
    def accepts(file: Path) -> bool:
        return file.suffix.lower() == ".pdf"

    def get_info(self, file: Path) -> dict[str, InfoValue]:
        with pymupdf.open(file) as pdf:
            page_count = pdf.page_count
            metadata = pdf.metadata if pdf.metadata else {}

        return {
            "page_count": page_count,
            "fomat": metadata.get("format"),
            "author": metadata.get("author"),
            "title": metadata.get("title"),
            "subject": metadata.get("subject"),
            "keywords": metadata.get("keywords"),
            "creator": metadata.get("creator"),
            "producer": metadata.get("producer"),
            "pdf_created": metadata.get("creationDate"),
            "pdf_modified": metadata.get("modDate"),
        }
