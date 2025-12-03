from openai import OpenAI


class BaseTranslator:
    """Base class for document translators with shared translation functionality."""

    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.translation_context = []  # Store previously translated segments for context

    def translate_text(self, text, target_language, use_context=True):
        """Translate text using OpenAI API with context preservation."""
        if not text.strip():
            return text

        # Build context from previous translations
        context_str = ""
        if use_context and self.translation_context:
            context_str = "\n\nPreviously translated segments (for consistency):\n"
            for orig, trans in self.translation_context[-5:]:  # Use last 5 translations
                context_str += f"Original: {orig}\nTranslation: {trans}\n\n"

        prompt = f"""Translate the following text to {target_language}.
Maintain the same tone, style, and any technical terms appropriately.
Only provide the translation, no explanations.{context_str}

Text to translate:
{text}"""

        response = self.client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4096
        )

        translated = response.choices[0].message.content.strip()

        # Store in context for consistency
        if use_context:
            self.translation_context.append((text[:200], translated[:200]))  # Store truncated versions

        return translated

    def translate_batch(self, paragraphs, target_language):
        """Translate multiple paragraphs in one API call."""
        if not paragraphs:
            return []

        # Build context from previous translations
        context_str = ""
        if self.translation_context:
            context_str = "\n\nPreviously translated segments (for consistency):\n"
            for orig, trans in self.translation_context[-3:]:  # Use last 3 translations
                context_str += f"Original: {orig}\nTranslation: {trans}\n\n"

        # Create numbered list of paragraphs
        numbered_text = ""
        for i, para in enumerate(paragraphs, 1):
            numbered_text += f"[{i}] {para}\n\n"

        prompt = f"""Translate the following paragraphs to {target_language}.
Maintain the same tone, style, and any technical terms appropriately.
Return ONLY the translations in the same numbered format, preserving the paragraph numbers.{context_str}

Paragraphs to translate:
{numbered_text}"""

        response = self.client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=8192
        )

        translated_text = response.choices[0].message.content.strip()

        # Parse the numbered responses
        translations = []
        lines = translated_text.split('\n')
        current_translation = ""

        for line in lines:
            # Check if line starts with a paragraph number
            if line.strip().startswith('[') and ']' in line:
                # Save previous translation if exists
                if current_translation:
                    translations.append(current_translation.strip())
                # Start new translation (remove the number)
                current_translation = line.split(']', 1)[1].strip() if ']' in line else ""
            else:
                # Continue current translation
                if current_translation or line.strip():
                    current_translation += " " + line.strip() if current_translation else line.strip()

        # Add the last translation
        if current_translation:
            translations.append(current_translation.strip())

        # Store in context for consistency
        if paragraphs and translations:
            self.translation_context.append((paragraphs[0][:200], translations[0][:200]))

        return translations
