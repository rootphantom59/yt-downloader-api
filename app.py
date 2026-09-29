from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# পাবলিক কোবাল্ট ইন্সট্যান্স
COBALT_API = "https://api.cobalt.tools"

@app.route('/download', methods=['GET', 'POST'])
def download():
    data = request.get_json(silent=True) or {}
    url = request.args.get('url') or data.get('url') or data.get('video_url') or request.form.get('url')
    
    if not url:
        return jsonify({"error": "Missing parameters"}), 400

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    payload = {
        "url": url,
        "videoQuality": "720",
        "youtubeVideoCodec": "h264"
    }

    try:
        # কোবাল্ট সার্ভার থেকে সরাসরি ভিডিও লিংক সংগ্রহ
        r = requests.post(f"{COBALT_API}/", json=payload, headers=headers, timeout=20)
        res_data = r.json()
        
        # সফলভাবে লিংক পেলে
        if res_data.get("status") in ["stream", "redirect", "tunnel"]:
            return jsonify({
                "status": "success",
                "url": res_data.get("url"),
                "title": res_data.get("filename", "YouTube Video")
            })
        elif res_data.get("text"):
            return jsonify({"error": res_data.get("text")}), 400
        else:
            return jsonify({"error": "Failed to extract video stream"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
