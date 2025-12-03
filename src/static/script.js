document.getElementById('translateForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById('file');
    const targetLanguage = document.getElementById('target_language').value;
    const submitBtn = document.getElementById('submitBtn');
    const statusDiv = document.getElementById('status');
    const progressDiv = document.getElementById('progress');

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

    // Show progress
    submitBtn.disabled = true;
    submitBtn.textContent = 'Translating...';
    statusDiv.classList.add('hidden');
    progressDiv.classList.remove('hidden');

    try {
        const response = await fetch('/translate', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        progressDiv.classList.add('hidden');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Translate Document';

        if (response.ok && data.success) {
            showStatus(
                `Translation complete! <a href="${data.download_url}">Download translated document</a>`,
                'success'
            );
            fileInput.value = ''; // Clear file input
        } else {
            showStatus(`Error: ${data.error || 'Unknown error occurred'}`, 'error');
        }
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
