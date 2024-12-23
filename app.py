from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import tempfile
import os
import re

app = Flask(__name__)

# GitHub 저장소의 cookies.txt 파일 경로
COOKIES_PATH = os.path.join(os.path.dirname(__file__), './cookies.txt')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    if not url or not re.match(r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$', url):
        return jsonify({"status": "error", "message": "유효한 YouTube URL을 입력하세요!"})

    with tempfile.TemporaryDirectory() as temp_dir:
        def progress_hook(d):
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', '0%').strip('%')
                print(f"다운로드 중... {percent}%")

        # ydl 옵션 설정
        ydl_opts = {
            'format': 'mp4/bestvideo+bestaudio/best',
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'progress_hooks': [progress_hook],
            'ignoreerrors': True,
            'no_warnings': True,
            'socket_timeout': 400  # 네트워크 타임아웃 설정
        }

        # 쿠키 파일 설정
        if os.path.exists(COOKIES_PATH):
            ydl_opts['cookiefile'] = COOKIES_PATH

        try:
            print(f"쿠키 파일 경로: {COOKIES_PATH}")
            print(f"쿠키 파일 존재 여부: {os.path.exists(COOKIES_PATH)}")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    # 동영상 정보 가져오기
                    info = ydl.extract_info(url, download=False)
                    if not info:
                        return jsonify({"status": "error", "message": "동영상 정보를 가져올 수 없습니다."})

                    # 동영상 다운로드
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)

                    # 파일 확인 후 전송
                    if os.path.exists(filename):
                        return send_file(
                            filename,
                            as_attachment=True,
                            download_name=os.path.basename(filename)
                        )
                    else:
                        return jsonify({"status": "error", "message": "파일 다운로드에 실패했습니다."})

                except yt_dlp.utils.DownloadError as e:
                    print(f"다운로드 오류: {e}")
                    return jsonify({"status": "error", "message": f"다운로드 오류: {str(e)}"})

        except Exception as e:
            print(f"처리 중 오류가 발생했습니다: {e}")
            return jsonify({"status": "error", "message": f"처리 중 오류가 발생했습니다: {str(e)}"})

if __name__ == '__main__':
    # 애플리케이션 실행
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
