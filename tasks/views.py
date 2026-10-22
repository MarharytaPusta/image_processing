from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ImageTask

@login_required
def index(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('image')

        if uploaded_file:
            ImageTask.objects.create(user=request.user, original_image=uploaded_file, status='pending'
            )
            return redirect('index')
    return render(request, 'tasks/index.html')