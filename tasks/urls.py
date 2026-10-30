from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/task/<int:task_id>/', views.get_task_status, name='task_status_single'),
    path('api/tasks/', views.get_all_tasks_status, name='tasks_status_all'),
    path('cancel/<int:task_id>/', views.cancel_task, name='cancel_task'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='tasks/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]