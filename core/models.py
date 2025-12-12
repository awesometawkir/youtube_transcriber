
from django.db import models
import uuid

class TranscriptionJob(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending') # pending, downloading, transcribing, completed, error
    progress = models.IntegerField(default=0)
    message = models.CharField(max_length=255, default='Waiting to start...')
    result_content = models.TextField(blank=True, null=True)
    output_format = models.CharField(max_length=10, default='txt')
    
    def __str__(self):
        return f"{self.id} - {self.status}"
