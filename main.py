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
        yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')
        audio_stream = yt.streams.filter(only_audio=True).first()
        if not audio_stream:
            return jsonify({'error': 'No audio stream found'}), 404

        filename = f'{video_id}.mp4'
        audio_stream.download(filename=filename)

        with open(filename, 'rb') as f:
            files = {'file': (filename, f)}
            res = requests.post('https://store1.gofile.io/uploadFile', files=files)

        os.remove(filename)
        time.sleep(5)

        if res.status_code == 200:
            file_url = res.json()['data']['downloadPage']
            return jsonify({'audio_url': file_url})
        else:
            return jsonify({'error': 'Upload failed'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
