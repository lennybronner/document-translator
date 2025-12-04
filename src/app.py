from flask import Flask, request, render_template, send_file, jsonify
import os
import uuid
import threading
import logging
from werkzeug.utils import secure_filename
from translator import DocumentTranslator
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Output to console
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DOWNLOAD_FOLDER'] = 'downloads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create folders if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'docx', 'doc', 'pdf', 'pptx'}

# Store translation job progress
translation_jobs = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

def translate_in_background(job_id, input_path, output_path, target_language, model_provider):
    """Background translation function."""
    try:
        def progress_callback(percent, message):
            translation_jobs[job_id]['progress'] = percent
            translation_jobs[job_id]['message'] = message

        # Build model configuration based on provider
        model_config = {'provider': model_provider}

        if model_provider == 'openai':
            model_config['api_key'] = os.getenv('OPENAI_API_KEY')
            model_config['model'] = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        elif model_provider == 'anthropic':
            model_config['api_key'] = os.getenv('ANTHROPIC_API_KEY')
            model_config['model'] = os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')
        elif model_provider == 'ollama':
            model_config['ollama_base_url'] = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
            model_config['model'] = os.getenv('OLLAMA_MODEL', 'llama3')

        translator = DocumentTranslator(model_config)
        translator.translate_document(input_path, output_path, target_language, progress_callback)

        # Clean up input file
        os.remove(input_path)

        translation_jobs[job_id]['progress'] = 100
        translation_jobs[job_id]['status'] = 'completed'
        translation_jobs[job_id]['message'] = 'Translation complete!'

    except Exception as e:
        translation_jobs[job_id]['status'] = 'error'
        translation_jobs[job_id]['error'] = str(e)
        translation_jobs[job_id]['message'] = f'Error: {str(e)}'


@app.route('/translate', methods=['POST'])
def translate():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    target_language = request.form.get('target_language', 'Spanish')
    model_provider = request.form.get('model_provider', 'openai')

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not supported. Supported types: .docx, .doc, .pdf, .pptx'}), 400

    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        job_id = str(uuid.uuid4())
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}_{filename}")
        file.save(input_path)

        output_filename = f"translated_{filename}"
        output_path = os.path.join(app.config['DOWNLOAD_FOLDER'], output_filename)

        # Initialize job tracking
        translation_jobs[job_id] = {
            'status': 'processing',
            'progress': 0,
            'message': 'Starting translation...',
            'output_filename': output_filename
        }

        # Start translation in background thread
        thread = threading.Thread(
            target=translate_in_background,
            args=(job_id, input_path, output_path, target_language, model_provider)
        )
        thread.start()

        return jsonify({
            'success': True,
            'job_id': job_id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/progress/<job_id>')
def get_progress(job_id):
    """Get the progress of a translation job."""
    if job_id not in translation_jobs:
        return jsonify({'error': 'Job not found'}), 404

    job = translation_jobs[job_id]
    response = {
        'status': job['status'],
        'progress': job['progress'],
        'message': job.get('message', '')
    }

    if job['status'] == 'completed':
        response['download_url'] = f"/download/{job['output_filename']}"
    elif job['status'] == 'error':
        response['error'] = job.get('error', 'Unknown error')

    return jsonify(response)

@app.route('/download/<filename>')
def download(filename):
    # Use absolute path for downloads
    file_path = os.path.abspath(os.path.join(app.config['DOWNLOAD_FOLDER'], filename))
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
