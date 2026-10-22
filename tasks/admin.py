from django.contrib import admin
from .models import ImageTask


@admin.register(ImageTask)
class ImageTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'progress', 'uploaded_at')

    list_filter = ('status', 'uploaded_at')

    search_fields = ('user__username',)