document.getElementById('translateForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById('file');
    const targetLanguage = document.getElementById('target_language').value;
    const modelProvider = document.getElementById('model_provider').value;
    const submitBtn = document.getElementById('submitBtn');
    const statusDiv = document.getElementById('status');
    const progressDiv = document.getElementById('progress');
    const progressBar = progressDiv.querySelector('.progress-bar');
    const progressText = progressDiv.querySelector('.progress-text');

    // Validate file
    if (!fileInput.files || fileInput.files.length === 0) {
        showStatus('Please select a file', 'error');
        return;
    }

    const file = fileInput.files[0];
    const maxSize = 16 * 1024 * 1024; // 16MB

    if (file.size > maxSize) {
        showStatus('File is too large. Maximum size is 16MB', 'error');
        return;
    }

    // Prepare form data
    const formData = new FormData();
    formData.append('file', file);
    formData.append('target_language', targetLanguage);
    formData.append('model_provider', modelProvider);

    // Show progress
    submitBtn.disabled = true;
    submitBtn.textContent = 'Translating...';
    statusDiv.classList.add('hidden');
    progressDiv.classList.remove('hidden');
    progressBar.style.width = '0%';
    progressText.textContent = 'Starting translation...';

    try {
        // Start translation
        const response = await fetch('/translate', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            progressDiv.classList.add('hidden');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Translate Document';
            showStatus(`Error: ${data.error || 'Unknown error occurred'}`, 'error');
            return;
        }

        // Poll for progress
        const jobId = data.job_id;
        const pollInterval = setInterval(async () => {
            try {
                const progressResponse = await fetch(`/progress/${jobId}`);
                const progressData = await progressResponse.json();

                // Update progress bar and text
                progressBar.style.width = `${progressData.progress}%`;
                progressText.textContent = progressData.message || 'Translating...';

                // Check if completed
                if (progressData.status === 'completed') {
                    clearInterval(pollInterval);
                    progressDiv.classList.add('hidden');
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Translate Document';
                    showStatus(
                        `Translation complete! <a href="${progressData.download_url}">Download translated document</a>`,
                        'success'
                    );
                    fileInput.value = ''; // Clear file input
                } else if (progressData.status === 'error') {
                    clearInterval(pollInterval);
                    progressDiv.classList.add('hidden');
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Translate Document';
                    showStatus(`Error: ${progressData.error || 'Translation failed'}`, 'error');
                }
            } catch (error) {
                clearInterval(pollInterval);
                progressDiv.classList.add('hidden');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Translate Document';
                showStatus(`Error: ${error.message}`, 'error');
            }
        }, 1000); // Poll every second

    } catch (error) {
        progressDiv.classList.add('hidden');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Translate Document';
        showStatus(`Error: ${error.message}`, 'error');
    }
});

function showStatus(message, type) {
    const statusDiv = document.getElementById('status');
    statusDiv.innerHTML = message;
    statusDiv.className = `status ${type}`;
    statusDiv.classList.remove('hidden');
}
