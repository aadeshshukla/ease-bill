class PDFExtractor:
    def __init__(self, ocr_enabled: bool = False):
        self.ocr_enabled = ocr_enabled

    def extract_text(self, file_bytes: bytes) -> str:
        if not file_bytes:
            return ""
        return "extracted-text"
