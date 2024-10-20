import zipfile
import xml.etree.ElementTree as ET
import os

def extract_office_metadata(file_path):
    """
    Extracts metadata from .docx, .pptx, and .xlsx files.

    Parameters:
        file_path (str): Path to the Office file.

    Returns:
        dict: A dictionary containing metadata and specific information based on file type.
              Common keys include title, subject, creator, keywords, description,
              last_modified_by, revision, created, modified.
              Additional keys:
                  - 'num_slides' for .pptx files
                  - 'num_sheets' for .xlsx files
    """
    # Validate file existence
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")

    # Supported file extensions
    supported_extensions = ['.docx', '.pptx', '.xlsx']
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext not in supported_extensions:
        raise ValueError(f"Unsupported file extension '{ext}'. Supported extensions are: {supported_extensions}")

    # Initialize metadata dictionary
    metadata = {}

    try:
        with zipfile.ZipFile(file_path, 'r') as office_file:
            # === Extract Core Properties ===
            try:
                with office_file.open('docProps/core.xml') as core_xml:
                    tree = ET.parse(core_xml)
                    root = tree.getroot()

                    # Define namespaces
                    namespaces = {
                        'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
                        'dc': 'http://purl.org/dc/elements/1.1/',
                        'dcterms': 'http://purl.org/dc/terms/',
                        'dcmitype': 'http://purl.org/dc/dcmitype/',
                        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
                    }

                    # Helper function to safely extract text
                    def get_text(element, path, namespaces):
                        found = element.find(path, namespaces)
                        return found.text if found is not None else None

                    # Extract common core properties
                    metadata['title'] = get_text(root, 'dc:title', namespaces)
                    metadata['subject'] = get_text(root, 'dc:subject', namespaces)
                    metadata['creator'] = get_text(root, 'dc:creator', namespaces)
                    metadata['keywords'] = get_text(root, 'cp:keywords', namespaces)
                    metadata['description'] = get_text(root, 'dc:description', namespaces)
                    metadata['last_modified_by'] = get_text(root, 'cp:lastModifiedBy', namespaces)
                    metadata['revision'] = get_text(root, 'cp:revision', namespaces)

                    # Extract creation and modification dates
                    created = root.find('dcterms:created', namespaces)
                    if created is not None and 'xsi:type' in created.attrib:
                        metadata['created'] = created.text
                    else:
                        metadata['created'] = None

                    modified = root.find('dcterms:modified', namespaces)
                    if modified is not None and 'xsi:type' in modified.attrib:
                        metadata['modified'] = modified.text
                    else:
                        metadata['modified'] = None

            except KeyError:
                # core.xml not found
                print("Warning: 'docProps/core.xml' not found in the archive.")
            
            # === Extract Specific Metadata Based on File Type ===
            if ext == '.pptx':
                # Count number of slides
                slide_files = [f for f in office_file.namelist() if f.startswith('ppt/slides/slide') and f.endswith('.xml')]
                metadata['num_slides'] = len(slide_files)

            elif ext == '.xlsx':
                # Count number of sheets
                try:
                    with office_file.open('xl/workbook.xml') as workbook_xml:
                        tree = ET.parse(workbook_xml)
                        root = tree.getroot()

                        # Define namespaces
                        namespaces = {
                            'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
                        }

                        sheets = root.find('main:sheets', namespaces)
                        if sheets is not None:
                            metadata['num_sheets'] = len(sheets.findall('main:sheet', namespaces))
                        else:
                            metadata['num_sheets'] = 0
                except KeyError:
                    print("Warning: 'xl/workbook.xml' not found in the archive.")
                    metadata['num_sheets'] = 0

            elif ext == '.docx':
                # Number of pages is not stored; set to None or omit
                metadata['num_pages'] = None

    except zipfile.BadZipFile:
        raise zipfile.BadZipFile(f"The file '{file_path}' is not a valid ZIP archive or is corrupted.")

    return metadata

# === Example Usage ===
if __name__ == "__main__":
    # Replace with your Office file paths
    office_files = [
        'example.docx',
        'example.pptx',
        'example.xlsx'
    ]

    for file in office_files:
        print(f"\nProcessing '{file}':")
        try:
            meta = extract_office_metadata(file)
            for key, value in meta.items():
                print(f"  {key}: {value}")
        except Exception as e:
            print(f"  Error: {e}")