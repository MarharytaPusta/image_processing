from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import ImageTask
from .process_image import start_background_processing

@login_required
def index(request):
    all_tasks = ImageTask.objects.filter(user=request.user).order_by('-id')
    latest_task = all_tasks.first()

    if request.method == 'POST':
        uploaded_file = request.FILES.get('image')
        if uploaded_file:
            task = ImageTask.objects.create(user=request.user, original_image=uploaded_file, status='pending')
            start_background_processing(task.id)
            return redirect('index')

    return render(request, 'tasks/index.html', {'task': latest_task, 'history_tasks': all_tasks})

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
def cancel_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(ImageTask, id=task_id, user=request.user)
        if task.status in ['pending', 'processing']:
            task.status = 'cancelled'
            task.save(update_fields=['status'])
    return redirect('index')