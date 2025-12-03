from docx import Document
from docx.shared import Pt, RGBColor
from copy import deepcopy
from .base import BaseTranslator


class DocxTranslator(BaseTranslator):
    """Translator for DOCX files with formatting preservation."""

    def translate(self, input_path, output_path, target_language):
        """Translate a DOCX file while preserving formatting."""
        doc = Document(input_path)
        new_doc = Document()

        # Copy styles and formatting
        self._copy_document_properties(doc, new_doc)

        # Copy numbering definitions for bullets and numbered lists
        self._copy_numbering_definitions(doc, new_doc)

        print(f"Translating document to {target_language}...")

        # Batch translate paragraphs
        BATCH_SIZE = 10
        paragraphs = doc.paragraphs
        total_paragraphs = len(paragraphs)

        i = 0
        while i < total_paragraphs:
            # Collect batch of paragraphs (including empty ones for order preservation)
            batch_paragraphs = []
            batch_info = []  # Store (index, text, is_empty)

            for j in range(i, min(i + BATCH_SIZE, total_paragraphs)):
                text = paragraphs[j].text
                if text.strip():
                    batch_paragraphs.append(text)
                    batch_info.append((j, text, False))
                else:
                    batch_info.append((j, "", True))

            # Translate batch
            if batch_paragraphs:
                print(f"Translating paragraphs {i+1}-{min(i + BATCH_SIZE, total_paragraphs)}/{total_paragraphs}...")
                translations = self.translate_batch(batch_paragraphs, target_language)

                # Create translation lookup
                translation_iter = iter(translations)

                # Apply translations in correct order
                for para_idx, text, is_empty in batch_info:
                    if is_empty:
                        # Add empty paragraph
                        new_doc.add_paragraph()
                    else:
                        # Add translated paragraph with formatting
                        translated_text = next(translation_iter)
                        new_paragraph = new_doc.add_paragraph()
                        self._copy_paragraph_format(paragraphs[para_idx], new_paragraph, translated_text)
            else:
                # All paragraphs in this batch are empty
                for para_idx, text, is_empty in batch_info:
                    new_doc.add_paragraph()

            i += BATCH_SIZE

        # Translate tables
        for table_idx, table in enumerate(doc.tables):
            print(f"Translating table {table_idx+1}/{len(doc.tables)}...")
            new_table = new_doc.add_table(rows=len(table.rows), cols=len(table.columns))

            for row_idx, row in enumerate(table.rows):
                for col_idx, cell in enumerate(row.cells):
                    if cell.text.strip():
                        translated_text = self.translate_text(cell.text, target_language)
                        new_table.rows[row_idx].cells[col_idx].text = translated_text
                        # Copy cell formatting
                        self._copy_cell_format(cell, new_table.rows[row_idx].cells[col_idx])

        new_doc.save(output_path)
        print(f"Translation complete! Saved to {output_path}")

    def _copy_document_properties(self, source_doc, target_doc):
        """Copy document-level properties."""
        # Copy sections (page layout, margins, etc.)
        for section in source_doc.sections:
            target_section = target_doc.sections[-1] if target_doc.sections else target_doc.add_section()
            target_section.page_height = section.page_height
            target_section.page_width = section.page_width
            target_section.left_margin = section.left_margin
            target_section.right_margin = section.right_margin
            target_section.top_margin = section.top_margin
            target_section.bottom_margin = section.bottom_margin

    def _copy_numbering_definitions(self, source_doc, target_doc):
        """Copy numbering definitions from source to target document."""
        try:
            # Access the numbering part of the document
            source_numbering_part = source_doc.part.numbering_part
            if source_numbering_part is None:
                return  # No numbering in source document

            # Copy the entire numbering element to the target document
            if not hasattr(target_doc.part, 'numbering_part') or target_doc.part.numbering_part is None:
                # Add numbering part to target by copying from source
                target_doc.part._element.body.addnext(deepcopy(source_numbering_part._element))
            else:
                # Replace existing numbering definitions
                target_doc.part.numbering_part._element.clear()
                for child in source_numbering_part._element:
                    target_doc.part.numbering_part._element.append(deepcopy(child))
        except Exception as e:
            print(f"Warning: Could not copy numbering definitions: {e}")
            # Continue without numbering definitions - paragraphs will still work but may have incorrect formatting

    def _copy_paragraph_format(self, source_para, target_para, text):
        """Copy paragraph formatting including runs (individual text formatting)."""
        # Copy style first (this includes list formatting)
        if source_para.style:
            try:
                target_para.style = source_para.style.name
            except:
                pass  # Style might not exist in new doc

        # Copy paragraph-level formatting
        target_para.alignment = source_para.alignment
        target_para.paragraph_format.left_indent = source_para.paragraph_format.left_indent
        target_para.paragraph_format.right_indent = source_para.paragraph_format.right_indent
        target_para.paragraph_format.first_line_indent = source_para.paragraph_format.first_line_indent
        target_para.paragraph_format.space_before = source_para.paragraph_format.space_before
        target_para.paragraph_format.space_after = source_para.paragraph_format.space_after
        target_para.paragraph_format.line_spacing = source_para.paragraph_format.line_spacing

        # Copy list/bullet formatting by copying the numbering properties
        source_pPr = source_para._element.pPr
        if source_pPr is not None:
            source_numPr = source_pPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr')
            if source_numPr is not None:
                # Get or create paragraph properties in target
                target_pPr = target_para._element.get_or_add_pPr()
                # Remove existing numPr if any
                existing_numPr = target_pPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr')
                if existing_numPr is not None:
                    target_pPr.remove(existing_numPr)
                # Copy the numbering properties
                target_pPr.append(deepcopy(source_numPr))

        # Apply uniform formatting from the first run
        # (inline formatting like bold/italic within paragraphs is not preserved)
        if source_para.runs:
            first_run = source_para.runs[0]
            run = target_para.add_run(text)

            # Copy run formatting from first run
            run.bold = first_run.bold
            run.italic = first_run.italic
            run.underline = first_run.underline

            if first_run.font.size:
                run.font.size = first_run.font.size
            if first_run.font.name:
                run.font.name = first_run.font.name
            if first_run.font.color.rgb:
                run.font.color.rgb = first_run.font.color.rgb
        else:
            target_para.add_run(text)

    def _copy_cell_format(self, source_cell, target_cell):
        """Copy cell formatting."""
        # Copy basic formatting - more advanced formatting could be added
        for source_para, target_para in zip(source_cell.paragraphs, target_cell.paragraphs):
            target_para.alignment = source_para.alignment
