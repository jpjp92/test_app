from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import tempfile
import os
from pathlib import Path

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    if not url:
        return jsonify({"status": "error", "message": "URL을 입력하세요!"})
    
    # 임시 디렉토리 사용
    with tempfile.TemporaryDirectory() as temp_dir:
        def progress_hook(d):
            if d['status'] == 'downloading':
                percent = d['_percent_str'].strip('%')
                print(f"다운로드 중... {percent}%")
        
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'progress_hooks': [progress_hook],
            # 쿠키 파일 경로 추가
            'cookiefile': 'cookies.txt',  # 쿠키 파일 경로
            # YouTube 인증 우회 옵션 추가
            'ignoreerrors': True,
            'no_warnings': True,
            'quiet': True,
            'no_check_certificate': True
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                return send_file(
                    filename,
                    as_attachment=True,
                    download_name=os.path.basename(filename)
                )
                
        except Exception as e:
            return jsonify({"status": "error", "message": f"다운로드 중 오류가 발생했습니다: {e}"})

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
