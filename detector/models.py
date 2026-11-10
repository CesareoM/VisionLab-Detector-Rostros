from django.db import models
class DetectionRecord(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    face_count = models.PositiveIntegerField()
    def __str__(self):
        return f'{self.created_at}: {self.face_count}'
