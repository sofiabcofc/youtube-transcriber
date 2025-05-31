from flask import Flask, request, jsonify
from pytube import YouTube

app = Flask(__name__)

@app.route('/get-audio-url', methods=['GET'])
def get_audio_url():
    print("DEBUG: /get-audio-url route called")
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "Missing 'url' parameter"}), 400
    try:
        yt = YouTube(video_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        return jsonify({
            "title": yt.title,
            "audio_url": audio_stream.url
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/')
def home():
    return "API is running!"
