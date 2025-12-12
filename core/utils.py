
import os
import yt_dlp
import whisper
import warnings
from django.conf import settings

# Suppress FP16 warning for CPU
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

def download_youtube_audio(url, output_path, progress_callback=None):
    """
    Downloads audio from a YouTube URL to the specified output path.
    Returns the path to the downloaded file.
    """
    
    def ydl_progress_hook(d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').replace('%','')
            try:
                if progress_callback:
                    progress_callback('downloading', int(float(p)))
            except:
                pass
        elif d['status'] == 'finished':
            if progress_callback:
                progress_callback('processing', 100)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [ydl_progress_hook],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        final_filename = os.path.splitext(filename)[0] + '.mp3'
        return final_filename

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def generate_srt_content(segments):
    srt_output = ""
    for i, segment in enumerate(segments):
        start = format_timestamp(segment['start'])
        end = format_timestamp(segment['end'])
        text = segment['text'].strip()
        srt_output += f"{i + 1}\n{start} --> {end}\n{text}\n\n"
    return srt_output

def transcribe_audio(file_path, model_name="base"):
    model = whisper.load_model(model_name)
    result = model.transcribe(file_path)
    return result
