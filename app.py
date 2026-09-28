from flask import Flask, request, jsonify
import yt_dlp
import requests
import os
import threading
import traceback

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

def download_and_send(chat_id, video_url):
    filename = f"video_{chat_id}.mp4"
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': f'video_{chat_id}.%(ext)s',
        'max_filesize': 48 * 1024 * 1024,
        'quiet': False,
        'no_warnings': False
    }

    try:
        print(f"[*] Downloading: {video_url} for chat_id: {chat_id}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        actual_file = filename
        for f in os.listdir():
            if f.startswith(f"video_{chat_id}"):
                actual_file = f
                break

        print(f"[*] Sending file: {actual_file} to Telegram...")
        telegram_api = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
        with open(actual_file, 'rb') as vf:
            res = requests.post(
                telegram_api,
                data={
                    'chat_id': chat_id,
                    'caption': '▶️ <b>YouTube ভিডিও ডাউনলোড সম্পন্ন!</b>',
                    'parse_mode': 'HTML'
                },
                files={'video': vf}
            )
            print(f"[*] Telegram response: {res.text}")

    except Exception as e:
        err_msg = str(e)
        print(f"[!] Error occurred: {err_msg}")
        traceback.print_exc()
        
        err_api = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(err_api, json={
            'chat_id': chat_id,
            'text': f'❌ এরর হয়েছে:\n<code>{err_msg[:200]}</code>',
            'parse_mode': 'HTML'
        })
    finally:
        for f in os.listdir():
            if f.startswith(f"video_{chat_id}"):
                try:
                    os.remove(f)
                except:
                    pass

@app.route('/download', methods=['POST'])
def handle_download():
    data = request.json or {}
    chat_id = data.get('chat_id')
    video_url = data.get('url')

    if not chat_id or not video_url:
        return jsonify({'error': 'Missing parameters'}), 400

    threading.Thread(target=download_and_send, args=(chat_id, video_url)).start()
    return jsonify({'status': 'processing'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
