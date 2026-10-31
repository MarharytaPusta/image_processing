document.addEventListener('DOMContentLoaded', function() {

const taskContainer = document.getElementById('task-container');

    if (taskContainer) {
        const taskId = taskContainer.dataset.taskId;
        let currentStatus = taskContainer.dataset.taskStatus;

        function checkSingleTaskStatus() {
            fetch(`/api/task/${taskId}/`)
                .then(response => response.json())
                .then(data => {
                    const progressBar = document.getElementById('progress-bar');
                    const statusText = document.getElementById('task-status');
                    const resultContainer = document.getElementById('result-container');
                    const resultImage = document.getElementById('result-image');
                    const cancelForm = document.getElementById('cancel-form');

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
                        if (cancelForm) cancelForm.style.display = 'none';
                        clearInterval(singleTaskTimer);
                    }
                    else if (currentStatus === 'failed' || currentStatus === 'cancelled') {
                        if (cancelForm) cancelForm.style.display = 'none';
                        clearInterval(singleTaskTimer);
                    }
                })
                .catch(error => console.error('Помилка AJAX (деталі):', error));
        }

        let singleTaskTimer;
        if (currentStatus === 'pending' || currentStatus === 'processing') {
            singleTaskTimer = setInterval(checkSingleTaskStatus, 1000);
        }
    }


    const tasksTable = document.getElementById('tasks-table');

    if (tasksTable) {
        const updateUrl = tasksTable.dataset.updateUrl;

        function checkAllTasksStatuses() {
            fetch(updateUrl)
                .then(response => response.json())
                .then(data => {
                    data.tasks.forEach(task => {

                        const statusCell = document.getElementById(`status-task-${task.id}`);
                        if (statusCell) {
                            if (task.status === 'completed') statusCell.innerHTML = '<span class="status-success">Завершено</span>';
                            else if (task.status === 'cancelled') statusCell.innerHTML = '<span class="status-cancelled">Скасовано</span>';
                            else if (task.status === 'failed') statusCell.innerHTML = '<span class="status-error">Помилка</span>';
                            else statusCell.innerHTML = '<span class="status-pending">У процесі...</span>';
                        }

                        const progressCell = document.getElementById(`progress-task-${task.id}`);
                        if (progressCell) {
                            if (task.status === 'completed') progressCell.innerText = '100%';
                            else if (task.status === 'cancelled' || task.status === 'failed') progressCell.innerText = '-';
                            else progressCell.innerText = task.progress + '%';
                        }

                        const resultCell = document.getElementById(`result-task-${task.id}`);
                        if (resultCell && task.status === 'completed' && task.processed_image_url) {
                            if (!resultCell.querySelector('a')) {
                                resultCell.innerHTML = `<a href="${task.processed_image_url}">Відкрити фото</a>`;
                            }
                        }
                    });
                })
                .catch(error => console.error('Помилка AJAX (таблиця):', error));
        }

        setInterval(checkAllTasksStatuses, 3000);
    }
});


document.getElementById('image_input')?.addEventListener('change', function() {
    const errBox = document.getElementById('error-container');
    const maxBytes = 2 * 1024 * 1024;

    if (this.files[0] && this.files[0].size > maxBytes) {
        errBox.innerText = 'Відмова: Файл занадто великий! Максимум 2 МБ.';
        errBox.style.display = 'block';
        this.value = '';
    } else {
        errBox.style.display = 'none';
    }
});