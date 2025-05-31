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
    try:
        data = request.get_json()
        print("Received data:", data)

        video_id = data.get('video_id')
        if not video_id:
            print("Missing video_id")
            return jsonify({'error': 'Missing video_id'}), 400

        print(f"Downloading audio for video_id: {video_id}")
        yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')
        audio_stream = yt.streams.filter(only_audio=True).first()

        if not audio_stream:
            print("No audio stream found")
            return jsonify({'error': 'No audio stream found'}), 404

        filename = f'{video_id}.mp4'
        audio_stream.download(filename=filename)
        print("Downloaded audio to", filename)

        import time
        time.sleep(10)  # To respect GoFile rate limits

        with open(filename, 'rb') as f:
            files = {'file': f}
            res = requests.post('https://store1.gofile.io/uploadFile', files=files)
            print("Upload response:", res.status_code, res.text)

        os.remove(filename)

        if res.status_code == 200:
            try:
                file_url = res.json()['data']['downloadPage']
                print("Uploaded file URL:", file_url)
                return jsonify({'audio_url': file_url})
            except Exception as e:
                print("Error parsing upload response JSON:", str(e))
                return jsonify({'error': 'Invalid upload response format'}), 500
        else:
            return jsonify({'error': 'Upload failed'}), 500

    except Exception as e:
        print("Unhandled exception:", str(e))
        return jsonify({'error': str(e)}), 500
