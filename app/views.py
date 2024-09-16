from django.shortcuts import render, redirect, get_list_or_404
from django.http import JsonResponse, HttpResponse
from .forms import VideoForm
from .models import Video, Subtitle
from app.tasks import extract_subtitles
from app.languages_code import LANGUAGE_NAMES
import os, re, time, subprocess, logging
from django.conf import settings
from moviepy.editor import VideoFileClip

logger = logging.getLogger(__name__)


def upload_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()
            process_video(video)
            return redirect('video_list')
    else:
        form = VideoForm()
    return render(request, 'upload.html', {'form': form})

def process_video(video_instance):
    input_file = video_instance.video_file.path
    # output_file = os.path.splitext(input_file)[0] + '.webm'

    output_dir = os.path.join(settings.MEDIA_ROOT, 'subtitles')
    os.makedirs(output_dir, exist_ok=True)
    subtitle_files = extract_subtitles(input_file, output_dir)

    for subtitle_file in subtitle_files:
        filename = os.path.basename(subtitle_file)
        lang_code = '_'.join(filename.split('_')[:3])

        Subtitle.objects.create(
                video=video_instance,
                language=lang_code,
                content=os.path.relpath(subtitle_file, settings.MEDIA_ROOT)
            )

    return input_file

def video_list(request):
    videos = Video.objects.all()
    return render(request, 'video_list.html', {'videos': videos})

def video_detail(request, video_id):
    video = Video.objects.get(id=video_id)
    search_query = request.GET.get('q', '').strip().lower()

    subtitles_with_names = []
    for subtitle in video.subtitles.filter(video=video):
        filename = os.path.basename(subtitle.content.name)
        base_name = filename.split('.')[0]
        language_code = base_name[-3:]
        language_name = LANGUAGE_NAMES().get(language_code, language_code)
        subtitles_with_names.append({
            'language': language_name,
            'content': subtitle.content.url
        })

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        results = []
        try:
            if search_query:
                seen_timestamps = set()
                for subtitle in video.subtitles.filter(video=video):
                    srt_path = subtitle.content.path
                    txt_path = os.path.join(settings.MEDIA_ROOT, 'subtitles', f"{video.id}_{base_name}.txt")
                    
                    if os.path.exists(txt_path):
                        os.remove(txt_path)
                        
                    convert_srt_to_txt(srt_path, txt_path)
                    
                    with open(txt_path, 'r', encoding='utf-8') as file:
                        content = file.read()

                    lines = content.splitlines()
                    timestamp = ''
                    
                    for line in lines:
                        line_lower = line.lower()
                        if '-->' in line:
                            timestamp = line
                        elif search_query in line_lower:
                            if timestamp not in seen_timestamps:
                                results.append({'timestamp': timestamp, 'line': line})
                                seen_timestamps.add(timestamp)
                                if len(results) >= 50:
                                    break
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return JsonResponse({'results': [], 'error': 'An error occurred'})
        return JsonResponse({'results': results})

    context = {
        'video': video,
        'subtitles_with_names': subtitles_with_names,
    }
    return render(request, 'video_detail.html', context)


def convert_srt_to_txt(srt_path, txt_path):
    with open(srt_path, 'r', encoding='utf-8') as srt_file:
        lines = srt_file.readlines()
    
    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        for line in lines:
            if line.strip().isdigit() or '-->' in line:
                txt_file.write(line)
            elif line.strip():
                txt_file.write(line)
