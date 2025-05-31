from flask import Flask, request, jsonify
from pytube import YouTube
import os
import requests
import time

app = Flask(__name__)

@app.route('/')
def index():
    return 'Flask is running!'

@app.route('/extract_audio', methods=['POST'])
def extract_audio():
    data = request.get_json()
    video_id = data.get('video_id')

    if not video_id:
        return jsonify({'error': 'Missing video_id'}), 400

    try:
        print(f"Received video_id: {video_id}")
        yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')
        audio_stream = yt.streams.filter(only_audio=True).first()
        if not audio_stream:
            return jsonify({'error': 'No audio stream found'}), 404

        filename = f'{video_id}.mp4'
        audio_stream.download(filename=filename)
        print(f"Downloaded audio to {filename}")

        time.sleep(10)  # Delay to avoid 429s on tmpfiles.org

        with open(filename, 'rb') as f:
            res = requests.post('https://tmpfiles.org/api/v1/upload', files={'file': f})

        os.remove(filename)

        if res.status_code == 200:
            file_url = res.json().get('data', {}).get('url')
            return jsonify({'audio_url': file_url})
        else:
            return jsonify({'error': 'Upload failed', 'details': res.text}), 500

    except Exception as e:
        print(f"Unhandled exception: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Required by Render
    app.run(host="0.0.0.0", port=port)
