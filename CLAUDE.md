# CLAUDE.md

## Project Overview

Document Translator — a Flask web app that translates DOCX files while preserving formatting, using OpenAI, Anthropic, or Ollama.

## Quick Commands

- `make setup` — create venv, install deps, create directories
- `make run` — start the Flask app on port 5000
- `make clean` — remove temp files and caches

## Architecture

```
src/app.py                      Flask routes + background thread job management
src/translator/__init__.py      DocumentTranslator factory (routes by file extension)
src/translator/base.py          BaseTranslator — multi-provider LLM calls, batching, context
src/translator/docx_translator.py  DOCX-specific translation with formatting preservation
```

- **Translation flow**: Upload → background thread → DocumentTranslator factory → DocxTranslator → BaseTranslator._call_llm() → save output
- **Batch translation**: Groups up to 20 paragraphs per API call with numbered format `[1] text`, parsed back with regex
- **Context window**: Last 5 translations (3 for batch) included in prompts for consistency
- **Formatting**: Creates a new Document, copies styles/numbering/properties from source via XML deep copy

## Key Patterns

- Progress tracking via callback + polling (`/progress/<job_id>`)
- Thread-safe job dict with `jobs_lock`
- XML namespace `{http://schemas.openxmlformats.org/wordprocessingml/2006/main}` used for numbering, borders, shading
- Batch parse fallback: regex → line-by-line → individual translation

## Environment

- Python, Flask, python-docx
- API keys in `.env` (see `.env.example`)
- No tests yet
