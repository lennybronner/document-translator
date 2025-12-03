# Document Translator

A web application that translates documents (DOCX, PDF, PPTX) while preserving their formatting using OpenAI GPT-5 Mini.

## Features

- **Format Preservation**: Maintains fonts, styles, paragraph formatting, and document structure
- **Context-Aware Translation**: Keeps translation consistent throughout the document by maintaining context
- **Multiple Languages**: Supports translation to/from multiple languages including Spanish, French, German, Chinese, Japanese, and more
- **Web Interface**: Simple, user-friendly web interface for uploading and downloading documents
- **Powered by GPT-5 Mini**: Uses OpenAI's GPT-5 Mini for high-quality translations

## Supported Formats

- **DOCX**: Full support with comprehensive formatting preservation
- **DOC**: Limited support (converted to DOCX format)
- **PDF**: Basic support (text extraction only, formatting may be lost)
- **PPTX**: Basic support (planned feature)

## Installation

### Prerequisites

- Python 3.8 or higher
- An OpenAI API key ([get one here](https://platform.openai.com/api-keys))

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

4. Add your OpenAI API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

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

3. Upload a document, select the target language, and click "Translate Document"

4. Download your translated document when processing is complete

## How It Works

1. **Document Parsing**: The application uses `python-docx` to parse DOCX files and extract text while preserving formatting information (fonts, styles, paragraph formatting, etc.)

2. **Translation**: Text is sent to OpenAI GPT-5 Mini for translation. The translator maintains a context window of recently translated segments to ensure consistency across the document.

3. **Format Recreation**: The translated text is inserted into a new document with the same formatting as the original (font sizes, styles, colors, alignment, spacing, etc.)

4. **Context Preservation**: Previously translated segments are included in the context when translating new segments, ensuring consistent terminology and style throughout the document.

## Project Structure

```
translator-claude/
├── Makefile              # Build and run commands
├── requirements.txt      # Python dependencies
├── .env.example         # Example environment variables
├── .gitignore
├── src/
│   ├── app.py           # Flask web application
│   ├── translator.py    # Core translation logic
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

- `OPENAI_API_KEY`: Your OpenAI API key (required)

### Flask Configuration

Edit [src/app.py](src/app.py) to modify:
- `MAX_CONTENT_LENGTH`: Maximum upload file size (default: 16MB)
- `UPLOAD_FOLDER`: Directory for temporary uploads
- `DOWNLOAD_FOLDER`: Directory for translated files

## Limitations

- **PDF Support**: PDF translation extracts text only and does not preserve formatting. For best results, use DOCX format.
- **Unsupported Document Elements**: The following Word document elements are not currently supported:
  - **Text boxes**: Text in text boxes/shapes will not be translated
  - **Table of Contents (TOC)**: TOC fields will not be translated or regenerated. You'll need to manually update the TOC in Word after translation (References → Update Table)
  - **Headers/Footers**: May not be fully preserved
  - **Embedded objects**: Charts, images with captions, SmartArt, etc. may not be handled correctly
- **Inline Formatting**: Bold, italic, and other formatting that changes within a paragraph is not preserved. Each paragraph will have uniform formatting based on its first character.
- **Complex Formatting**: Some advanced formatting features (custom styles, macros) may not be fully preserved
- **File Size**: Large documents may take longer to process and may exceed API rate limits
- **Language Detection**: Source language is auto-detected by GPT-5 Mini; manual specification is not currently supported

## Future Enhancements

- Full PDF support with formatting preservation
- PowerPoint (PPTX) translation support
- Batch processing for multiple files
- Progress tracking for long documents
- Support for more document formats
- Manual source language selection
- Translation memory/glossary support

## Troubleshooting

### "Module not found" errors
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### API key errors
Verify your `.env` file contains a valid OpenAI API key.

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
- [OpenAI GPT-5 Mini](https://openai.com/) - AI translation
