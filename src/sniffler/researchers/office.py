import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import olefile

from .base import InfoValue


class ModernOfficeResearcher:
    def accepts(self, file: Path) -> bool:
        return file.suffix.lower() in {".docx", ".pptx", ".xlsx"}

    def get_info(self, file: Path) -> dict[str, InfoValue]:
        reserved_keys = {"created", "modified"}
        metadata = {
            (f"office_{k}" if k in reserved_keys else k): v
            for k, v in extract_openxml_office_metadata(file).items()
        }
        return metadata


class LegacyOfficeResearcher:
    def accepts(self, file: Path) -> bool:
        return file.suffix.lower() in {".doc", ".ppt", ".xls"}

    def get_info(self, file: Path) -> dict[str, InfoValue]:
        reserved_keys = {"created", "modified"}
        metadata = {
            (f"office_{k}" if k in reserved_keys else k): v
            for k, v in extract_ole_office_metadata(file).items()
        }
        return metadata


def extract_openxml_office_metadata(file_path: Path) -> dict[str, InfoValue]:
    """
    Extracts metadata from an Office document (e.g., .docx, .pptx, .xlsx).
    """
    metadata = {}
    ext = file_path.suffix.lower()

    with zipfile.ZipFile(file_path, "r") as z:
        metadata.update(extract_core_properties(z))

        if ext == ".docx":
            metadata.update(extract_docx_metadata(z))
        elif ext == ".pptx":
            metadata.update(extract_pptx_metadata(z))
        elif ext == ".xlsx":
            metadata.update(extract_xlsx_metadata(z))

    return metadata


def extract_core_properties(z: zipfile.ZipFile) -> dict:
    metadata = {}
    with z.open("docProps/core.xml") as core_xml:
        tree = ET.parse(core_xml)
        root = tree.getroot()
        namespaces = {
            "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
            "dc": "http://purl.org/dc/elements/1.1/",
            "dcterms": "http://purl.org/dc/terms/",
        }

        tags = [
            ("dc", ["title", "subject", "creator", "description"]),
            ("cp", ["keywords", "lastModifiedBy", "revision"]),
            ("dcterms", ["created", "modified"]),
        ]

        for prefix, keys in tags:
            for key in keys:
                elem = root.find(f"{prefix}:{key}", namespaces)
                if elem is not None and elem.text:
                    metadata[key] = elem.text
    return metadata


def extract_docx_metadata(z: zipfile.ZipFile) -> dict:
    metadata = {}
    with z.open("docProps/app.xml") as app_xml:
        tree = ET.parse(app_xml)
        root = tree.getroot()
        namespaces = {
            "": "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties",
            "vt": "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes",
        }

        counts = {
            "Words": "word_count",
            "Characters": "char_count",
            "Pages": "page_count",
        }

        for tag, key in counts.items():
            elem = root.find(tag, namespaces)
            if elem is not None and elem.text:
                metadata[key] = int(elem.text)
    return metadata


def extract_pptx_metadata(z: zipfile.ZipFile) -> dict:
    slides = [
        f
        for f in z.namelist()
        if f.startswith("ppt/slides/slide") and f.endswith(".xml")
    ]
    return {"num_slides": len(slides)}


def extract_xlsx_metadata(z: zipfile.ZipFile) -> dict:
    metadata = {}
    with z.open("xl/workbook.xml") as workbook_xml:
        tree = ET.parse(workbook_xml)
        root = tree.getroot()
        namespaces = {"": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        sheets = root.findall(".//sheet", namespaces)
        metadata["num_sheets"] = len(sheets)
    return metadata


def extract_ole_office_metadata(file_path: Path) -> dict[str, InfoValue]:
    """
    Extracts metadata from older Office files (.doc, .xls, .ppt).

    Parameters:
        file_path (Path): Path to the Office file.

    Returns:
        dict: A dictionary containing metadata.
    """
    metadata = {}
    property_map = {
        2: "title",
        3: "subject",
        4: "author",
        5: "keywords",
        # 6: "comments",
        7: "template",
        8: "last_saved_by",
        9: "revision_number",
        12: "total_editing_time",
        13: "last_printed",
        14: "created",
        15: "last_saved",
        16: "page_count",
        # 17: "word_count",
        # 18: "char_count",
        # 19: "thumbnail",
        # 20: "app_name",
        # 21: "security",
    }
    try:
        with olefile.OleFileIO(str(file_path)) as ole:
            if not ole.exists("\x05SummaryInformation"):
                return metadata

            meta = ole.getproperties("\x05SummaryInformation")
            for prop_id, prop_name in property_map.items():
                if prop_id in meta:
                    value = meta[prop_id]
                    if isinstance(value, bytes):
                        value = value.decode("utf-8", errors="replace")
                    metadata[prop_name] = value

    except olefile.olefile.NotOleFileError:
        pass

    return metadata
