from flask import Flask, request, render_template, send_file, jsonify
import os
from werkzeug.utils import secure_filename
from translator import DocumentTranslator
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DOWNLOAD_FOLDER'] = 'downloads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create folders if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'docx', 'doc', 'pdf', 'pptx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    target_language = request.form.get('target_language', 'Spanish')

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not supported. Supported types: .docx, .doc, .pdf, .pptx'}), 400

    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)

        # Translate document
        translator = DocumentTranslator(os.getenv('OPENAI_API_KEY'))
        output_filename = f"translated_{filename}"
        output_path = os.path.join(app.config['DOWNLOAD_FOLDER'], output_filename)

        translator.translate_document(input_path, output_path, target_language)

        # Clean up input file
        os.remove(input_path)

        return jsonify({
            'success': True,
            'download_url': f'/download/{output_filename}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    # Use absolute path for downloads
    file_path = os.path.abspath(os.path.join(app.config['DOWNLOAD_FOLDER'], filename))
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
