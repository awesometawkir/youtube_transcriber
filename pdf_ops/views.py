
import os
import shutil
import uuid
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from .models import PDFText
from .utils import get_pdf_info, extract_pdf_text, split_pdf, unlock_pdf

def index(request):
    texts = PDFText.objects.all().order_by('-created_at')
    return render(request, 'pdf_ops/index.html', {'texts': texts})

def handle_upload(file):
    if not file:
        return None, None
    file_name = f"{uuid.uuid4()}_{file.name}"
    path = default_storage.save(os.path.join('pdf_uploads', file_name), ContentFile(file.read()))
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    return full_path, path

def split_view(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        parts = int(request.POST.get('parts', 2))
        
        full_path, rel_path = handle_upload(file)
        if not full_path:
            return JsonResponse({'error': 'No file provided'}, status=400)
            
        try:
            output_dir = os.path.join(settings.MEDIA_ROOT, 'pdf_split_output', str(uuid.uuid4()))
            os.makedirs(output_dir, exist_ok=True)
            
            files = split_pdf(full_path, parts, output_dir)
            
            # Generate URLs
            urls = [f"{settings.MEDIA_URL}pdf_split_output/{os.path.basename(output_dir)}/{f}" for f in files]
            
            return JsonResponse({'files': urls})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            if os.path.exists(full_path):
                os.remove(full_path)

def extract_view(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        
        full_path, rel_path = handle_upload(file)
        if not full_path:
            return JsonResponse({'error': 'No file provided'}, status=400)
            
        try:
            text = extract_pdf_text(full_path)
            
            # Save to DB
            PDFText.objects.create(title=file.name, content=text)
            
            return JsonResponse({'text': text})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            if os.path.exists(full_path):
                os.remove(full_path)

def unlock_view(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        
        full_path, rel_path = handle_upload(file)
        if not full_path:
            return JsonResponse({'error': 'No file provided'}, status=400)
            
        try:
            output_filename = f"unlocked_{uuid.uuid4()}.pdf"
            output_path = os.path.join(settings.MEDIA_ROOT, 'pdf_unlocked', output_filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            unlock_pdf(full_path, output_path)
            
            url = f"{settings.MEDIA_URL}pdf_unlocked/{output_filename}"
            return JsonResponse({'file': url})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            if os.path.exists(full_path):
                os.remove(full_path)

def delete_text_view(request, text_id):
    if request.method == 'POST':
        try:
            PDFText.objects.get(id=text_id).delete()
            return JsonResponse({'status': 'success'})
        except PDFText.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)
