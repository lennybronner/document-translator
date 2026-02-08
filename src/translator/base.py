import re

from openai import OpenAI
import anthropic
import requests
import logging

logger = logging.getLogger(__name__)


class BaseTranslator:
    """Base class for document translators with shared translation functionality."""

    def __init__(self, model_config, progress_callback=None):
        """
        Initialize translator with model configuration.

        model_config should be a dict with:
        - provider: 'openai', 'anthropic', or 'ollama'
        - api_key: API key for the provider (not needed for ollama)
        - model: specific model name (optional, uses defaults)
        - ollama_base_url: base URL for ollama (default: http://localhost:11434)
        """
        self.model_config = model_config
        self.provider = model_config.get('provider', 'openai')
        self.translation_context = []  # Store previously translated segments for context
        self.progress_callback = progress_callback

        # Initialize the appropriate client
        if self.provider == 'openai':
            self.client = OpenAI(api_key=model_config.get('api_key'))
            self.model = model_config.get('model', 'gpt-4.1-mini')
        elif self.provider == 'anthropic':
            self.client = anthropic.Anthropic(api_key=model_config.get('api_key'))
            self.model = model_config.get('model', 'claude-sonnet-4-5-20250929')
        elif self.provider == 'ollama':
            self.ollama_base_url = model_config.get('ollama_base_url', 'http://localhost:11434')
            self.model = model_config.get('model', 'qwen2.5:7b')
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _call_llm(self, prompt, max_tokens=4096):
        """Call the appropriate LLM based on provider."""
        if self.provider == 'openai':
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()

        elif self.provider == 'anthropic':
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()

        elif self.provider == 'ollama':
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()['response'].strip()

    def translate_text(self, text, target_language, use_context=True):
        """Translate text using configured LLM with context preservation."""
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
If the text contains HTML formatting tags (<b>, <i>, <u>), preserve them in your translation around the equivalent translated words. Never split a word across a tag boundary — always place opening and closing tags at word boundaries.
Only provide the translation, no explanations.{context_str}

Text to translate:
{text}"""

        translated = self._call_llm(prompt, max_tokens=4096)

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
If the text contains HTML formatting tags (<b>, <i>, <u>), preserve them in your translation around the equivalent translated words. Never split a word across a tag boundary — always place opening and closing tags at word boundaries.
Return ONLY the translations in the same numbered format, preserving the paragraph numbers.{context_str}

Paragraphs to translate:
{numbered_text}"""

        translated_text = self._call_llm(prompt, max_tokens=8192)

        # Parse the numbered responses more robustly
        translations = []

        # Try to extract numbered items using regex for better accuracy
        pattern = r'\[(\d+)\]\s*(.+?)(?=\[\d+\]|$)'
        matches = re.findall(pattern, translated_text, re.DOTALL)

        if matches and len(matches) == len(paragraphs):
            # Successfully parsed with regex
            for num, text in matches:
                translations.append(text.strip())
        else:
            # Fall back to line-by-line parsing
            logger.debug(f"Regex parsing found {len(matches) if matches else 0} items, expected {len(paragraphs)}, falling back to line parser")
            lines = translated_text.split('\n')
            current_translation = ""

            for line in lines:
                # Check if line starts with a paragraph number
                if line.strip().startswith('[') and ']' in line:
                    # Save previous translation if exists and not empty
                    if current_translation.strip():
                        translations.append(current_translation.strip())
                    # Start new translation (remove the number)
                    current_translation = line.split(']', 1)[1].strip() if ']' in line else ""
                else:
                    # Continue current translation
                    if line.strip():
                        current_translation += " " + line.strip() if current_translation else line.strip()

            # Add the last translation if not empty
            if current_translation.strip():
                translations.append(current_translation.strip())

        # Validate that we got the right number of translations
        if len(translations) != len(paragraphs):
            logger.warning(f"Batch translation mismatch - Provider: {self.provider}, Model: {self.model}")
            logger.warning(f"Expected {len(paragraphs)} translations but got {len(translations)}")
            logger.debug(f"Raw response (first 500 chars): {translated_text[:500]}")

            # Fall back to individual translation if batch failed
            logger.info("Falling back to individual translation for reliability")
            translations = []
            for para in paragraphs:
                translations.append(self.translate_text(para, target_language, use_context=False))

        # Store in context for consistency
        if paragraphs and translations:
            self.translation_context.append((paragraphs[0][:200], translations[0][:200]))

        return translations
