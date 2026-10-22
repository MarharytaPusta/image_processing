from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('status/<int:task_id>/', views.get_task_status, name='task_status'),
]