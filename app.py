from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/download', methods=['GET', 'POST'])
def download():
    data = request.get_json(silent=True) or {}
    url = request.args.get('url') or data.get('url') or data.get('video_url') or request.form.get('url')
    
    if not url:
        return jsonify({"error": "Missing parameters"}), 400

    try:
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios']
                }
            }
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            title = info.get('title', 'Video')
            
        return jsonify({
            "status": "success",
            "url": video_url,
            "title": title
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
