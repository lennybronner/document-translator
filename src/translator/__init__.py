import os
from .docx_translator import DocxTranslator


class DocumentTranslator:
    """Factory class for creating appropriate translator based on file type."""

    def __init__(self, model_config):
        self.model_config = model_config

    def translate_document(self, input_path, output_path, target_language, progress_callback=None):
        """Main entry point for document translation."""
        file_ext = os.path.splitext(input_path)[1].lower()

        if file_ext in ['.docx', '.doc']:
            translator = DocxTranslator(self.model_config, progress_callback)
            translator.translate(input_path, output_path, target_language)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")


__all__ = ['DocumentTranslator']
