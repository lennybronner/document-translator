import os
from .docx_translator import DocxTranslator
from .pdf_translator import PdfTranslator
from .pptx_translator import PptxTranslator


class DocumentTranslator:
    """Factory class for creating appropriate translator based on file type."""

    def __init__(self, api_key):
        self.api_key = api_key

    def translate_document(self, input_path, output_path, target_language):
        """Main entry point for document translation."""
        file_ext = os.path.splitext(input_path)[1].lower()

        if file_ext in ['.docx', '.doc']:
            translator = DocxTranslator(self.api_key)
            translator.translate(input_path, output_path, target_language)
        elif file_ext == '.pdf':
            # PDF output will be DOCX format
            if not output_path.endswith('.docx'):
                output_path = os.path.splitext(output_path)[0] + '.docx'
            translator = PdfTranslator(self.api_key)
            translator.translate(input_path, output_path, target_language)
        elif file_ext == '.pptx':
            translator = PptxTranslator(self.api_key)
            translator.translate(input_path, output_path, target_language)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")


__all__ = ['DocumentTranslator']
