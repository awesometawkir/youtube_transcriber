
import os
import threading
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .utils import download_youtube_audio, transcribe_audio, generate_srt_content
from .models import TranscriptionJob

import shutil

def cleanup_everything():
    # 1. Delete all Jobs from DB
    TranscriptionJob.objects.all().delete()
    
    # 2. Delete all files in Media Root
    media_root = settings.MEDIA_ROOT
    if os.path.exists(media_root):
        for filename in os.listdir(media_root):
            file_path = os.path.join(media_root, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")

def index(request):
    cleanup_everything()
    return render(request, 'core/index.html')

def process_transcription_thread(job_id, source_type, data, output_format):
    try:
        job = TranscriptionJob.objects.get(id=job_id)
        job.status = 'processing'
        job.message = 'Starting...'
        job.save()

        audio_path = ""
        
        # Callback for progress
        def update_progress(status, percent):
            job.status = status
            job.progress = percent
            job.message = f"{status.title()}... {percent}%"
            job.save()

        # Step 1: Obtain Audio
        if source_type == 'youtube':
            job.message = 'Downloading audio...'
            job.status = 'downloading'
            job.save()
            audio_path = download_youtube_audio(data, settings.MEDIA_ROOT, progress_callback=update_progress)
        
        elif source_type == 'file':
            # File is already saved in the main view, data is the path
            audio_path = data
            job.message = 'File uploaded.'
            job.save()

        # Step 2: Transcribe
        job.status = 'transcribing'
        job.message = 'Loading AI Model & Transcribing...'
        job.progress = 0
        job.save()
        
        result = transcribe_audio(audio_path)
        
        # Step 3: Format
        if output_format == 'srt':
            content = generate_srt_content(result['segments'])
        else:
            content = result['text']
        
        job.result_content = content
        job.status = 'completed'
        job.message = 'Done'
        job.progress = 100
        job.save()

        # Step 4: Cleanup
        if os.path.exists(audio_path):
            os.remove(audio_path)

    except Exception as e:
        job.status = 'error'
        job.message = str(e)
        job.save()

def transcribe(request):
    if request.method == 'POST':
        source_type = request.POST.get('source_type')
        output_format = request.POST.get('output_format', 'txt')
        
        # Create Job
        job = TranscriptionJob.objects.create(output_format=output_format)
        
        data = None
        
        if source_type == 'youtube':
            data = request.POST.get('youtube_url')
            if not data:
                return JsonResponse({'error': 'YouTube URL is required'}, status=400)
            
        elif source_type == 'file':
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return JsonResponse({'error': 'File is required'}, status=400)
            
            # Save properly to pass path to thread
            file_name = f"{job.id}_{uploaded_file.name}"
            path = default_storage.save(os.path.join('uploads', file_name), ContentFile(uploaded_file.read()))
            data = os.path.join(settings.MEDIA_ROOT, path)
            
        else:
            return JsonResponse({'error': 'Invalid source type'}, status=400)

        # Start Thread
        thread = threading.Thread(target=process_transcription_thread, args=(job.id, source_type, data, output_format))
        thread.start()
        
        return JsonResponse({'job_id': job.id})
        
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def check_status(request, job_id):
    try:
        job = TranscriptionJob.objects.get(id=job_id)
        return JsonResponse({
            'status': job.status,
            'progress': job.progress,
            'message': job.message,
            'result': job.result_content if job.status == 'completed' else None,
            'format': job.output_format
        })
    except TranscriptionJob.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)
