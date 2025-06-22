from django.db import models
from django.utils import timezone
from datetime import timedelta

def upload_path(instance, filename):
    return f'uploads/{instance.id}/{filename}'

class EditedImage(models.Model):
    original_image = models.ImageField(upload_to=upload_path)
    removed_bg_image = models.ImageField(upload_to=upload_path, null=True, blank=True)
    edited_image = models.ImageField(upload_to=upload_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # def is_expired(self):
    #     return timezone.now() > self.created_at + timedelta(hours=24)
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

    def delete_files_and_self(self):
        if self.original_image:
            self.original_image.delete(save=False)
        if self.removed_bg_image:
            self.removed_bg_image.delete(save=False)
        if self.edited_image:
            self.edited_image.delete(save=False)
        self.delete()
