from flask import Flask, render_template, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

# 다운로드할 폴더 설정
DOWNLOAD_FOLDER = "./유튜브_다운로더"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    if not url:
        return jsonify({"status": "error", "message": "URL을 입력하세요!"})

    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = d['_percent_str'].strip('%')
            print(f"다운로드 중... {percent}%")

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'progress_hooks': [progress_hook],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return jsonify({"status": "success", "message": "영상이 성공적으로 다운로드되었습니다!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"다운로드 중 오류가 발생했습니다: {e}"})

if __name__ == '__main__':
    app.run(debug=True)
