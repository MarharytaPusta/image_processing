from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from pathlib import Path
import os
from .models import ImageTask
from .process_image import start_background_processing
from django.conf import settings


@login_required
def index(request):
    server_name = os.getenv('SERVER_NAME', 'Server')
    error_message = None

    all_tasks = ImageTask.objects.filter(user=request.user).order_by('-id')
    latest_task = all_tasks.first()

    if request.method == 'POST':
        uploaded_file = request.FILES.get('image')

        all_tasks = list(all_tasks)

        success_tasks_count = ImageTask.objects.filter(
            user=request.user,
            status__in=['pending', 'processing', 'completed']
        ).count()

        if success_tasks_count >= settings.MAX_TASKS:
            error_message = f"Відмова: перевищено ліміт ({settings.MAX_TASKS} задач)"

        elif uploaded_file and uploaded_file.size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            error_message = f"Відмова: файл занадто великий. Максимальний розмір — {settings.MAX_FILE_SIZE_MB} МБ."

        suffixes = [s.lower() for s in Path(uploaded_file.name).suffixes]
        if not suffixes or suffixes[-1] not in settings.ALLOWED_EXTENSIONS or len(suffixes) > 1:
            error_message = f"Відмова: неприпустимий формат файлу. Дозволені: {', '.join(settings.ALLOWED_EXTENSIONS)}"

        elif uploaded_file:
            task = ImageTask.objects.create(user=request.user, original_image=uploaded_file, status='pending')
            start_background_processing(task.id)
            return redirect('index')


    return render(request, 'tasks/index.html', {'task': latest_task, 'history_tasks': all_tasks, 'error_message': error_message, 'server_name': server_name, "max_file_size_mb" : settings.MAX_FILE_SIZE_MB,})

@login_required
def get_task_status(request, task_id):
    try:
        task = ImageTask.objects.get(id=task_id, user=request.user)
        return JsonResponse({
            'status': task.status,
            'progress': task.progress,
            'processed_image_url': task.processed_image.url if task.processed_image else None
        })
    except ImageTask.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)


@login_required
def get_all_tasks_status(request):
    tasks = ImageTask.objects.filter(user=request.user)

    tasks_data = []
    for task in tasks:
        tasks_data.append({
            'id': task.id,
            'status': task.status,
            'progress': task.progress,
            'processed_image_url': task.processed_image.url if task.processed_image else None
        })

    return JsonResponse({'tasks': tasks_data})


@login_required
def cancel_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(ImageTask, id=task_id, user=request.user)
        if task.status in ['pending', 'processing']:
            task.status = 'cancelled'
            task.save(update_fields=['status'])
    return redirect('index')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()

    return render(request, 'tasks/register.html', {'form': form})