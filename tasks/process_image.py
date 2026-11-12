import threading
from io import BytesIO
from PIL import Image
import logging
from django.core.files.base import ContentFile
from .models import ImageTask


logger = logging.getLogger('image_processing')


def process_image_task(task_id):
    try:
        task = ImageTask.objects.get(id=task_id)
        task.status = 'processing'
        task.save()

        image_data = task.original_image.read()
        img = Image.open(BytesIO(image_data))

        img = img.convert('RGB')
        width, height = img.size

        processed_img = Image.new('RGB', (width, height))
        pixels = processed_img.load()
        original_pixels = img.load()

        total_pixels = width * height
        processed_count = 0
        last_reported_progress = 0

        for y in range(height):
            for x in range(width):
                r, g, b = original_pixels[x, y]

                new_r = min(255, int(r * 1.5))
                new_g = min(255, int(g * 1.5))
                new_b = min(255, int(b * 1.5))

                pixels[x, y] = (new_r, new_g, new_b)
                processed_count += 1

            for i in range(2000000):
                if i != 1:
                    pass

            current_progress = int((processed_count / total_pixels) * 100)

            if current_progress > last_reported_progress:
                task.refresh_from_db()

                if task.status == 'cancelled':
                    return

                task.progress = current_progress
                task.save(update_fields=['progress', 'last_updated_at'])
                last_reported_progress = current_progress

        buffer = BytesIO()
        processed_img.save(buffer, format='JPEG')

        new_filename = f"processed_{task.id}.jpg"
        task.processed_image.save(new_filename, ContentFile(buffer.getvalue()), save=False)

        task.status = 'completed'
        task.progress = 100
        task.save()

    except Exception as e:
        task.status = 'failed'
        task.save()
        logger.error(f"Error in task {task_id}: {e}")


def start_background_processing(task_id):
    thread = threading.Thread(target=process_image_task, args=(task_id,))
    thread.daemon = True
    thread.start()