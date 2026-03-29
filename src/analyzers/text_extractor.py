"""
Text extraction from images, PDFs, Word documents, and Excel spreadsheets.
"""

from __future__ import annotations

from contextlib import nullcontext
from pathlib import Path
from typing import Any

# OCR and PDF imports
try:
    import pytesseract
    from PIL import Image
    import pypdf
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True

    # HEIC support for OCR
    try:
        from pillow_heif import register_heif_opener
        register_heif_opener()
    except ImportError:
        pass  # HEIC support optional for OCR
except ImportError:
    OCR_AVAILABLE = False

# Word document imports
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Excel imports
try:
    from openpyxl import load_workbook
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

# Cost tracking imports (optional)
try:
    from cost_roi_calculator import CostTracker
except ImportError:
    class CostTracker:  # type: ignore[no-redef]
        """Stub CostTracker when cost tracking is not available."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def __enter__(self) -> "CostTracker":
            return self

        def __exit__(self, *args: Any) -> bool:
            return False


_MAX_PDF_PAGES = 10
_MAX_PDF_OCR_PAGES = 5
_MIN_PDF_TEXT_LENGTH = 100
_MAX_XLSX_SHEETS = 5
_MAX_XLSX_ROWS = 100
_MAX_TEXT_BYTES = 50_000


class TextExtractor:
    """Extract text content from various file formats."""

    def __init__(self, cost_calculator: Any | None = None) -> None:
        self.cost_calculator = cost_calculator
        self.ocr_available = OCR_AVAILABLE

    def extract_text_from_image(self, image_path: Path) -> str:
        """Extract text from image using OCR."""
        if not self.ocr_available:
            return ""

        with CostTracker(self.cost_calculator, 'tesseract_ocr') if self.cost_calculator else nullcontext():
            try:
                image = Image.open(image_path)
                text = pytesseract.image_to_string(image)
                return text.strip()
            except Exception as e:
                print(f"  OCR error: {e}")
                return ""

    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF (searchable or scanned)."""
        if not self.ocr_available:
            return ""

        with CostTracker(self.cost_calculator, 'pdf_extraction') if self.cost_calculator else nullcontext():
            text = ""

            try:
                with open(pdf_path, 'rb') as f:
                    reader = pypdf.PdfReader(f)
                    for page in reader.pages[:_MAX_PDF_PAGES]:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"

                if len(text.strip()) > _MIN_PDF_TEXT_LENGTH:
                    return text.strip()

                print(f"  Using OCR for scanned PDF...")
                images = convert_from_path(pdf_path, first_page=1, last_page=_MAX_PDF_OCR_PAGES)
                for image in images:
                    text += pytesseract.image_to_string(image) + "\n"

                return text.strip()
            except Exception as e:
                print(f"  PDF extraction error: {e}")
                return ""

    def extract_text_from_docx(self, docx_path: Path) -> str:
        """Extract text from Word document."""
        if not DOCX_AVAILABLE:
            return ""

        with CostTracker(self.cost_calculator, 'docx_extraction') if self.cost_calculator else nullcontext():
            try:
                doc = Document(docx_path)
                text = []
                for paragraph in doc.paragraphs:
                    if paragraph.text.strip():
                        text.append(paragraph.text)

                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            if cell.text.strip():
                                text.append(cell.text)

                return "\n".join(text)
            except Exception as e:
                print(f"  DOCX extraction error: {e}")
                return ""

    def extract_text_from_xlsx(self, xlsx_path: Path) -> str:
        """Extract text from Excel spreadsheet."""
        if not EXCEL_AVAILABLE:
            return ""

        with CostTracker(self.cost_calculator, 'xlsx_extraction') if self.cost_calculator else nullcontext():
            try:
                workbook = load_workbook(xlsx_path, read_only=True, data_only=True)
                text = []

                for sheet_name in workbook.sheetnames[:_MAX_XLSX_SHEETS]:
                    sheet = workbook[sheet_name]
                    for row in sheet.iter_rows(max_row=_MAX_XLSX_ROWS, values_only=True):
                        row_text = ' '.join([str(cell) for cell in row if cell is not None])
                        if row_text.strip():
                            text.append(row_text)

                workbook.close()
                return "\n".join(text)
            except Exception as e:
                print(f"  XLSX extraction error: {e}")
                return ""

    def extract_text(self, file_path: Path, mime_type: str | None = None) -> str:
        """Extract text from various file types.

        Args:
            file_path: Path to the file.
            mime_type: Optional pre-detected MIME type. When omitted the
                       caller is responsible for passing it; pass an empty
                       string to skip MIME-based routing.
        """
        file_ext = file_path.suffix.lower()

        if mime_type and mime_type.startswith('image/'):
            return self.extract_text_from_image(file_path)
        elif mime_type == 'application/pdf' or file_ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_ext in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            return self.extract_text_from_xlsx(file_path)
        elif (mime_type and mime_type.startswith('text/')) or file_ext in ['.txt', '.md', '.csv']:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read(_MAX_TEXT_BYTES)
            except Exception:
                return ""

        return ""
