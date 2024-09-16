from django.db import models
import os
from django.conf import settings

class Video(models.Model):
    title = models.CharField(max_length=255, unique=True)
    video_file = models.FileField(upload_to='videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Subtitle(models.Model):
    video = models.ForeignKey(Video, related_name='subtitles', on_delete=models.CASCADE)
    language = models.CharField(max_length=50)
    content = models.FileField(upload_to='subtitles/')
    created_at = models.DateTimeField(auto_now_add=True)
