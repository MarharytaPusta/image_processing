document.addEventListener('DOMContentLoaded', function() {
    const taskContainer = document.getElementById('task-container');

    if (!taskContainer) return;

    const taskId = taskContainer.dataset.taskId;
    let currentStatus = taskContainer.dataset.taskStatus;

    function checkStatus() {
        fetch(`/status/${taskId}/`)
            .then(response => response.json())
            .then(data => {
                const progressBar = document.getElementById('progress-bar');
                const statusText = document.getElementById('task-status');
                const resultContainer = document.getElementById('result-container');
                const resultImage = document.getElementById('result-image');

                progressBar.style.width = data.progress + '%';
                progressBar.textContent = data.progress + '%';

                const statusTranslations = {
                    'pending': 'В черзі',
                    'processing': 'Обробляється',
                    'completed': 'Завершено',
                    'failed': 'Помилка',
                    'cancelled': 'Скасовано'
                };
                statusText.textContent = statusTranslations[data.status] || data.status;
                currentStatus = data.status;

                if (currentStatus === 'completed') {
                    if (data.processed_image_url) {
                        resultImage.src = data.processed_image_url;
                        resultContainer.style.display = 'block';
                    }
                    clearInterval(pollingTimer);
                } else if (currentStatus === 'failed' || currentStatus === 'cancelled') {
                    progressBar.style.backgroundColor = '#f44336';
                    clearInterval(pollingTimer);
                }
            })
            .catch(error => console.error('Помилка AJAX:', error));
    }

    let pollingTimer;
    if (currentStatus === 'pending' || currentStatus === 'processing') {
        pollingTimer = setInterval(checkStatus, 1000);
    }
});