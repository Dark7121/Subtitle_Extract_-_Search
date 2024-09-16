from django.urls import path
from .views import upload_video, video_list, video_detail

urlpatterns = [
    path('upload/', upload_video, name='upload_video'),
    path('videos/', video_list, name='video_list'),
    path('videos/<int:video_id>/', video_detail, name='video_detail')
]
