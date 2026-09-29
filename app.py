from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

def get_yt_id(url):
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/|youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

@app.route('/download', methods=['GET', 'POST'])
def download():
    data = request.get_json(silent=True) or {}
    url = request.args.get('url') or data.get('url') or data.get('video_url') or request.form.get('url')
    
    if not url:
        return jsonify({"error": "Missing parameters"}), 400

    vid = get_yt_id(url)
    if not vid:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    clean_url = f"https://www.youtube.com/watch?v={vid}"

    # পাবলিক প্রক্সি গেটওয়ে ১: Siputzx
    try:
        r = requests.get(f"https://api.siputzx.my.id/api/d/ytmp4?url={clean_url}", timeout=20)
        res = r.json()
        if res.get("status") and res.get("data", {}).get("dl"):
            return jsonify({
                "status": "success",
                "url": res["data"]["dl"],
                "title": res["data"].get("title", "YouTube Video")
            })
    except Exception:
        pass

    # পাবলিক প্রক্সি গেটওয়ে ২: Agatz
    try:
        r = requests.get(f"https://api.agatz.xyz/api/ytmp4?url={clean_url}", timeout=20)
        res = r.json()
        if res.get("status") == 200 and res.get("data", {}).get("downloadUrl"):
            return jsonify({
                "status": "success",
                "url": res["data"]["downloadUrl"],
                "title": res["data"].get("title", "YouTube Video")
            })
    except Exception:
        pass

    # পাবলিক প্রক্সি গেটওয়ে ৩: Widipe
    try:
        r = requests.get(f"https://widipe.com/download/ytdl?url={clean_url}", timeout=20)
        res = r.json()
        if res.get("result", {}).get("mp4"):
            return jsonify({
                "status": "success",
                "url": res["result"]["mp4"],
                "title": res["result"].get("title", "YouTube Video")
            })
    except Exception:
        pass

    return jsonify({"error": "সবগুলো গেটওয়ে বর্তমানে ব্যস্ত, কিছুক্ষণ পর চেষ্টা করুন"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
