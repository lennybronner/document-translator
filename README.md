# Document Translator

A web application that translates DOCX documents while preserving their formatting using multiple AI models.

## Features

- **Multiple AI Models**: Choose from OpenAI GPT-4.1 Mini, Anthropic Claude Sonnet 4.5, or local Llama 3 via Ollama
- **Format Preservation**: Maintains fonts, styles, paragraph formatting, and document structure
- **Table Support**: Preserves table formatting including borders, cell shading, and merged cells
- **Context-Aware Translation**: Keeps translation consistent throughout the document by maintaining context
- **Batch Translation**: Processes multiple paragraphs and table cells together for faster translation
- **Real-time Progress Tracking**: Visual progress bar shows translation status
- **Multiple Languages**: Supports translation to/from multiple languages including Spanish, French, German, Chinese, Japanese, and more
- **Web Interface**: Simple, user-friendly web interface for uploading and downloading documents
- **Privacy Options**: Use local models with Ollama for complete privacy and offline capability

## Supported Formats

- **DOCX**: Full support with comprehensive formatting preservation including tables, bullets, numbering, and cell formatting
- **DOC**: Limited support (converted to DOCX format)

## Installation

### Prerequisites

- Python 3.8 or higher
- At least one of the following:
  - An OpenAI API key ([get one here](https://platform.openai.com/api-keys))
  - An Anthropic API key ([get one here](https://console.anthropic.com/))
  - Ollama installed locally ([setup guide](OLLAMA_SETUP.md))

### Setup

1. Clone this repository or download the files

2. Run the setup (creates venv and installs dependencies):
   ```bash
   make setup
   ```

3. Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```

4. Add your API key(s) to the `.env` file:
   ```
   # For OpenAI
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4.1-mini

   # For Anthropic
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ANTHROPIC_MODEL=claude-sonnet-4-5-20250929

   # For Ollama (local model)
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3
   ```

   **Note**: You only need to configure the API key for the model you plan to use.

#### Alternative Setup (without Make)

If you don't have Make installed:

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create necessary directories:
   ```bash
   mkdir -p uploads downloads
   ```

## Usage

1. Start the Flask server:
   ```bash
   make run
   ```

   Or without Make:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python src/app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Choose your translation settings:
   - **Select Document**: Upload a .docx or .doc file
   - **Target Language**: Choose the language to translate to
   - **Translation Model**: Select which AI model to use
     - **OpenAI GPT-4.1 Mini**: Fast, cost-effective, requires OpenAI API key
     - **Anthropic Claude Sonnet 4.5**: High quality, requires Anthropic API key
     - **Local Llama 3 (Ollama)**: Free, private, offline - requires [Ollama setup](OLLAMA_SETUP.md)

4. Click "Translate Document" and wait for processing

5. Download your translated document when processing is complete

## Choosing a Translation Model

| Model | Speed | Quality | Cost | Privacy | Notes |
|-------|-------|---------|------|---------|-------|
| **OpenAI GPT-4.1 Mini** | Fast | Excellent | ~$0.15-0.60/1M tokens | Cloud-based | Best overall balance |
| **Claude Sonnet 4.5** | Fast | Excellent | ~$3.00/1M tokens | Cloud-based | Best for complex texts |
| **Llama 3 (Ollama)** | Medium | Very Good | Free | 100% local | Best for privacy/offline |

For getting started, we recommend **OpenAI GPT-4.1 Mini** for the best balance of speed, quality, and cost.

For complete privacy and offline use, see our [Ollama Setup Guide](OLLAMA_SETUP.md).

## How It Works

1. **Document Parsing**: The application uses `python-docx` to parse DOCX files and extract text while preserving formatting information (fonts, styles, paragraph formatting, etc.)

2. **Translation**: Text is sent to your chosen AI model (OpenAI, Anthropic, or Ollama) for translation. The translator maintains a context window of recently translated segments to ensure consistency across the document.

3. **Format Recreation**: The translated text is inserted into a new document with the same formatting as the original (font sizes, styles, colors, alignment, spacing, etc.)

4. **Context Preservation**: Previously translated segments are included in the context when translating new segments, ensuring consistent terminology and style throughout the document.

## Project Structure

```
translator-claude/
├── Makefile              # Build and run commands
├── requirements.txt      # Python dependencies
├── .env.example         # Example environment variables
├── OLLAMA_SETUP.md      # Ollama installation guide
├── .gitignore
├── src/
│   ├── app.py           # Flask web application
│   ├── translator/
│   │   ├── __init__.py         # DocumentTranslator factory
│   │   ├── base.py             # BaseTranslator with multi-model support
│   │   └── docx_translator.py  # DOCX translation
│   ├── templates/
│   │   └── index.html   # Web interface
│   └── static/
│       ├── style.css    # Styling
│       └── script.js    # Frontend logic
├── uploads/             # Temporary storage for uploaded files
└── downloads/           # Temporary storage for translated files
```

## Configuration

### Environment Variables

**OpenAI Configuration:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: Model to use (default: `gpt-4.1-mini`)

**Anthropic Configuration:**
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `ANTHROPIC_MODEL`: Model to use (default: `claude-sonnet-4-5-20250929`)

**Ollama Configuration:**
- `OLLAMA_BASE_URL`: Ollama server URL (default: `http://localhost:11434`)
- `OLLAMA_MODEL`: Model to use (default: `llama3`)

### Flask Configuration

Edit [src/app.py](src/app.py) to modify:
- `MAX_CONTENT_LENGTH`: Maximum upload file size (default: 16MB)
- `UPLOAD_FOLDER`: Directory for temporary uploads
- `DOWNLOAD_FOLDER`: Directory for translated files

## Limitations

- **Unsupported Document Elements**: The following Word document elements are not currently supported:
  - **Text boxes**: Text in text boxes/shapes will not be translated
  - **Table of Contents (TOC)**: TOC fields will not be translated or regenerated. You'll need to manually update the TOC in Word after translation (References → Update Table)
  - **Headers/Footers**: May not be fully preserved
  - **Embedded objects**: Charts, images with captions, SmartArt, etc. may not be handled correctly
- **Inline Formatting**: Bold, italic, and other formatting that changes within a paragraph is not preserved. Each paragraph will have uniform formatting based on its first character.
- **Complex Formatting**: Some advanced formatting features (custom styles, macros) may not be fully preserved
- **File Size**: Large documents may take longer to process and may exceed API rate limits
- **Language Detection**: Source language is auto-detected by the AI model; manual specification is not currently supported

## Future Enhancements

- PDF and PowerPoint (PPTX) translation support
- Batch processing for multiple files
- Manual source language selection
- Translation memory/glossary support
- Support for text boxes and embedded objects
- Header/footer translation
- Table of Contents regeneration

## Troubleshooting

### "Module not found" errors
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### API key errors
- For OpenAI: Verify your `.env` file contains a valid `OPENAI_API_KEY`
- For Anthropic: Verify your `.env` file contains a valid `ANTHROPIC_API_KEY`
- For Ollama: Ensure Ollama is running (`ollama serve`) and the model is downloaded (`ollama pull llama3`)

### File upload errors
Check that the `uploads/` and `downloads/` directories exist and have write permissions. You can create them with:
```bash
mkdir -p uploads downloads
```

Or use the Makefile:
```bash
make setup
```

## Available Make Commands

- `make setup` - Create virtual environment, install dependencies, and create necessary directories
- `make install` - Install/update dependencies
- `make run` - Run the Flask application
- `make clean` - Remove uploaded/downloaded files and Python cache

## License

MIT License - feel free to use and modify as needed.

## Credits

Built with:
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [python-docx](https://python-docx.readthedocs.io/) - Document processing
- [OpenAI](https://openai.com/) - GPT-4.1 Mini AI translation
- [Anthropic](https://anthropic.com/) - Claude Sonnet 4.5 AI translation
- [Ollama](https://ollama.ai/) - Local Llama 3 model support
