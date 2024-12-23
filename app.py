from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import tempfile
import os
import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import threading

app = Flask(__name__)
COOKIES_PATH = os.path.join(os.path.dirname(__file__), './cookies.txt')
DOWNLOAD_TIMEOUT = 180  # 3분 타임아웃

def download_video_with_timeout(url, temp_dir, ydl_opts):
    def download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info), info
    
    with ThreadPoolExecutor() as executor:
        future = executor.submit(download)
        try:
            filename, info = future.result(timeout=DOWNLOAD_TIMEOUT)
            return filename, info
        except TimeoutError:
            raise Exception("다운로드 시간이 초과되었습니다. 나중에 다시 시도해주세요.")

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    if not url or not re.match(r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$', url):
        return jsonify({"status": "error", "message": "유효한 YouTube URL을 입력하세요!"})

    with tempfile.TemporaryDirectory() as temp_dir:
        ydl_opts = {
            'format': 'mp4/bestvideo+bestaudio/best',
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'ignoreerrors': True,
            'no_warnings': True,
            'socket_timeout': 30  # 소켓 타임아웃 30초로 감소
        }

        if os.path.exists(COOKIES_PATH):
            ydl_opts['cookiefile'] = COOKIES_PATH

        try:
            filename, info = download_video_with_timeout(url, temp_dir, ydl_opts)
            
            if os.path.exists(filename):
                return send_file(
                    filename,
                    as_attachment=True,
                    download_name=os.path.basename(filename)
                )
            else:
                return jsonify({"status": "error", "message": "파일 다운로드에 실패했습니다."})
                
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)


# from flask import Flask, render_template, request, jsonify, send_file
# import yt_dlp
# import tempfile
# import os

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/download', methods=['POST'])
# def download_video():
#     url = request.form.get('url')
#     if not url:
#         return jsonify({"status": "error", "message": "URL을 입력하세요!"})
    
#     with tempfile.TemporaryDirectory() as temp_dir:
#         def progress_hook(d):
#             if d['status'] == 'downloading':
#                 percent = d['_percent_str'].strip('%')
#                 print(f"다운로드 중... {percent}%")
        
#         ydl_opts = {
#             'format': 'mp4/bestvideo+bestaudio/best',  # format 옵션 수정
#             'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
#             'merge_output_format': 'mp4',
#             'progress_hooks': [progress_hook],
#             'ignoreerrors': True,
#             'no_warnings': True
#         }
        
#         try:
#             with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#                 # 먼저 정보 추출 시도
#                 try:
#                     info = ydl.extract_info(url, download=False)
#                     if info is None:
#                         return jsonify({"status": "error", "message": "동영상 정보를 가져올 수 없습니다."})
                    
#                     # 정보 추출 성공 시 다운로드 진행
#                     info = ydl.extract_info(url, download=True)
#                     filename = ydl.prepare_filename(info)
                    
#                     if os.path.exists(filename):
#                         return send_file(
#                             filename,
#                             as_attachment=True,
#                             download_name=os.path.basename(filename)
#                         )
#                     else:
#                         return jsonify({"status": "error", "message": "파일 다운로드에 실패했습니다."})
                        
#                 except yt_dlp.utils.DownloadError as e:
#                     return jsonify({"status": "error", "message": f"다운로드 오류: {str(e)}"})
                
#         except Exception as e:
#             return jsonify({"status": "error", "message": f"처리 중 오류가 발생했습니다: {str(e)}"})

# if __name__ == '__main__':
#     app.run(debug=True)


# from flask import Flask, render_template, request, jsonify, send_file
# import yt_dlp
# import tempfile
# import os

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/download', methods=['POST'])
# def download_video():
#     url = request.form.get('url')
#     if not url:
#         return jsonify({"status": "error", "message": "URL을 입력하세요!"})
    
#     # 임시 디렉토리 사용
#     with tempfile.TemporaryDirectory() as temp_dir:
#         def progress_hook(d):
#             if d['status'] == 'downloading':
#                 percent = d['_percent_str'].strip('%')
#                 print(f"다운로드 중... {percent}%")
        
#         ydl_opts = {
#             'format': 'bestvideo+bestaudio/best',
#             'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
#             'merge_output_format': 'mp4',
#             'progress_hooks': [progress_hook],
#         }
        
#         try:
#             with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#                 info = ydl.extract_info(url, download=True)
#                 filename = ydl.prepare_filename(info)
                
#                 # 파일을 클라이언트에게 직접 전송
#                 return send_file(
#                     filename,
#                     as_attachment=True,
#                     download_name=os.path.basename(filename)
#                 )
                
#         except Exception as e:
#             return jsonify({"status": "error", "message": f"다운로드 중 오류가 발생했습니다: {e}"})

# if __name__ == '__main__':
#     app.run(debug=True)

# from flask import Flask, render_template, request, jsonify
# import yt_dlp
# import os

# app = Flask(__name__)

# # 다운로드할 폴더 설정
# DOWNLOAD_FOLDER = "./유튜브_다운로더"
# os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/download', methods=['POST'])
# def download_video():
#     url = request.form.get('url')
#     if not url:
#         return jsonify({"status": "error", "message": "URL을 입력하세요!"})

#     def progress_hook(d):
#         if d['status'] == 'downloading':
#             percent = d['_percent_str'].strip('%')
#             print(f"다운로드 중... {percent}%")

#     ydl_opts = {
#         'format': 'bestvideo+bestaudio/best',
#         'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
#         'merge_output_format': 'mp4',
#         'progress_hooks': [progress_hook],
#     }

#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             ydl.download([url])
#         return jsonify({"status": "success", "message": "영상이 성공적으로 다운로드되었습니다!"})
#     except Exception as e:
#         return jsonify({"status": "error", "message": f"다운로드 중 오류가 발생했습니다: {e}"})

# if __name__ == '__main__':
#     app.run(debug=True)
