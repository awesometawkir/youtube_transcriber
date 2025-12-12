
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from core.models import TranscriptionJob
from pdf_ops.models import PDFText
from .models import TextSnippet
from .services import MODELS, generate_summary

def index(request):
    # Fetch available context sources
    transcriptions = TranscriptionJob.objects.filter(status='completed').order_by('-created_at')
    pdf_texts = PDFText.objects.all().order_by('-created_at')
    snippets = TextSnippet.objects.all().order_by('-created_at')
    
    context = {
        'models': MODELS,
        'transcriptions': transcriptions,
        'pdf_texts': pdf_texts,
        'snippets': snippets
    }
    return render(request, 'summarizer/index.html', context)

def summarize_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text')
            context_ids = data.get('context_ids', []) # List of "pdf_1", "job_2", "snip_3"
            model = data.get('model')
            provider = data.get('provider')
            api_key = data.get('api_key')

            if not text and not context_ids:
                 return JsonResponse({'error': 'No text or context provided'}, status=400)

            # Resolve Contexts
            context_list = []
            for cid in context_ids:
                type_, id_ = cid.split('_')
                try:
                    if type_ == 'pdf':
                        item = PDFText.objects.get(id=id_)
                        context_list.append(f"PDF Title: {item.title}\nContent: {item.content}")
                    elif type_ == 'job':
                        item = TranscriptionJob.objects.get(id=id_)
                        context_list.append(f"Transcription: {item.id}\nContent: {item.result_content}")
                    elif type_ == 'snip':
                        item = TextSnippet.objects.get(id=id_)
                        context_list.append(f"Snippet: {item.title}\nContent: {item.content}")
                except Exception:
                    continue 

            result = generate_summary(text, context_list, model, api_key, provider)
            
            if 'error' in result:
                return JsonResponse({'error': result['error']}, status=400)
            
            return JsonResponse({'summary': result['result']})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def create_snippet(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title', 'Untitled')
            content = data.get('content')
            if not content:
                return JsonResponse({'error': 'Content is required'}, status=400)
            
            snippet = TextSnippet.objects.create(title=title, content=content)
            return JsonResponse({'id': snippet.id, 'title': snippet.title, 'created_at': snippet.created_at.strftime("%b %d")})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def delete_context(request, type_, id_):
    if request.method == 'POST':
        try:
            if type_ == 'pdf':
                PDFText.objects.get(id=id_).delete()
            elif type_ == 'snip':
                TextSnippet.objects.get(id=id_).delete()
            # We assume user can't delete 'job' from here, or we can allow it if needed. kept strictly for pdf/snip for now as per request.
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
