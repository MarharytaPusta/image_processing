from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ImageTask
from .process_image import start_background_processing

@login_required
def index(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('image')

        if uploaded_file:
            task = ImageTask.objects.create(user=request.user, original_image=uploaded_file, status='pending'
            )
            start_background_processing(task.id)
            return redirect('index')
    return render(request, 'tasks/index.html')