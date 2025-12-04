from docx import Document
import PyPDF2
from .base import BaseTranslator


class PdfTranslator(BaseTranslator):
    """Translator for PDF files (extracts text to DOCX format)."""

    def translate(self, input_path, output_path, target_language):
        """Translate a PDF file to DOCX (formatting may be lost)."""
        print(f"Translating PDF to {target_language}...")
        print("Note: PDF translation extracts text only. Formatting will be lost.")

        # Extract text from PDF
        with open(input_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)

            if self.progress_callback:
                self.progress_callback(5, "Extracting text from PDF...")

            # Create new DOCX document
            new_doc = Document()

            # Process each page
            for page_num in range(total_pages):
                print(f"Translating page {page_num + 1}/{total_pages}...")

                # Report progress (pages are 5-95% of total progress)
                if self.progress_callback:
                    progress = 5 + int((page_num / total_pages) * 90)
                    self.progress_callback(progress, f"Translating page {page_num + 1}/{total_pages}...")

                page = pdf_reader.pages[page_num]
                text = page.extract_text()

                if text.strip():
                    # Split into paragraphs (by double newlines or single newlines)
                    paragraphs = text.split('\n\n')
                    for para in paragraphs:
                        para = para.strip()
                        if para:
                            translated = self.translate_text(para, target_language)
                            new_doc.add_paragraph(translated)

                # Add page break except for last page
                if page_num < total_pages - 1:
                    new_doc.add_page_break()

            if self.progress_callback:
                self.progress_callback(95, "Saving document...")

        new_doc.save(output_path)
        print(f"Translation complete! Saved to {output_path}")
