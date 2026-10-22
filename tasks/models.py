from django.db import models


class ImageTask(models.Model):
    STATUS_CHOICES = (
        ('pending', 'В черзі'),
        ('processing', 'Обробляється'),
        ('completed', 'Завершено'),
        ('failed', 'Помилка'),
        ('cancelled', 'Скасовано'),
    )

    original_image = models.ImageField(upload_to='images/originals/')
    processed_image = models.ImageField(upload_to='images/processed/', null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField(default=0)

    uploaded_at = models.DateTimeField(auto_now_add=True)  # Фіксується один раз при створенні
    last_updated_at = models.DateTimeField(auto_now=True)  # Оновлюється при кожній зміні відсотка
    finished_at = models.DateTimeField(null=True, blank=True)  # Заповнимо вручну, коли задача завершиться

    def __str__(self):
        return f"Task {self.id} - {self.get_status_display()} ({self.progress}%)"