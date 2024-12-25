# app.py
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import tempfile
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError

app = Flask(__name__)
COOKIES_PATH = os.path.join(os.path.dirname(__file__), './cookies.txt')
DOWNLOAD_TIMEOUT = 300

def get_video_info(url, ydl_opts):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

# def download_video(url, temp_dir, progress_hook):
#     ydl_opts = {
#         'format': 'bestvideo[ext=mp4][height>=1080]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
#         'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
#         'merge_output_format': 'mp4',
#         'progress_hooks': [progress_hook],
#         'socket_timeout': 30
#     }
    
#     if os.path.exists(COOKIES_PATH):
#         ydl_opts['cookiefile'] = COOKIES_PATH
        
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         info = ydl.extract_info(url, download=True)
#         filename = ydl.prepare_filename(info)
#         # mp4_ 제거
#         if filename.endswith('.mp4_.mp4'):
#             new_filename = filename.replace('.mp4_.mp4', '.mp4')
#             os.rename(filename, new_filename)
#             return new_filename
#         return filename

# def download_video(url, temp_dir, progress_hook):
#     ydl_opts = {
#         'format': 'bestvideo[ext=mp4][height>=1080]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
#         'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
#         'merge_output_format': 'mp4',
#         'progress_hooks': [progress_hook],
#         'socket_timeout': 30,
#         'throttledratelimit': 100000,
#         'sleep_interval': 2,
#         'max_sleep_interval': 5,
#         'nocheckcertificate': True,
#         'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#     }
    
#     if os.path.exists(COOKIES_PATH):
#         ydl_opts['cookiefile'] = COOKIES_PATH
        
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         try:
#             info = ydl.extract_info(url, download=True)
#             filename = ydl.prepare_filename(info)
            
#             if filename.endswith('.mp4_.mp4'):
#                 new_filename = filename.replace('.mp4_.mp4', '.mp4')
#                 os.rename(filename, new_filename)
#                 return new_filename
#             return filename
            
#         except Exception as e:
#             print(f"Download error: {str(e)}")
#             raise

def download_video(url, temp_dir, progress_hook):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4][height>=1080]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'progress_hooks': [progress_hook],
        'socket_timeout': 60,
        'retries': 10,
        'fragment_retries': 10,
        'retry_sleep_functions': {'http': lambda n: 10},
        'throttledratelimit': 50000,
        'sleep_interval': 10,
        'max_sleep_interval': 20,
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {
                'skip': ['webpage', 'dash', 'hls'],
                'player_skip': ['webpage', 'configs']
            }
        },
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    if os.path.exists(COOKIES_PATH):
        ydl_opts['cookiefile'] = COOKIES_PATH
        
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            time.sleep(5)  # Rate limiting
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if filename.endswith('.mp4_.mp4'):
                new_filename = filename.replace('.mp4_.mp4', '.mp4')
                os.rename(filename, new_filename)
                return new_filename
            return filename
            
        except Exception as e:
            print(f"Download error: {str(e)}")
            raise


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video_route():
    url = request.form.get('url')
    if not url or not re.match(r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$', url):
        return jsonify({"status": "error", "message": "유효한 YouTube URL을 입력하세요!"})

    progress = {"percent": 0}
    
    def progress_hook(d):
        if d['status'] == 'downloading':
            progress["percent"] = float(d.get('_percent_str', '0%').strip('%'))

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            with ThreadPoolExecutor() as executor:
                future = executor.submit(download_video, url, temp_dir, progress_hook)
                filename = future.result(timeout=DOWNLOAD_TIMEOUT)
                
                if os.path.exists(filename):
                    return send_file(
                        filename,
                        as_attachment=True,
                        download_name=os.path.basename(filename)
                    )
                
                return jsonify({"status": "error", "message": "파일 다운로드 실패"})
                
        except TimeoutError:
            return jsonify({"status": "error", "message": "다운로드 시간 초과 (5분)"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
