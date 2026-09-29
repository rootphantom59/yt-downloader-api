from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

def extract_video_id(url):
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/|youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

@app.route('/download', methods=['GET', 'POST'])
def download():
    data = request.get_json(silent=True) or {}
    url = request.args.get('url') or data.get('url') or data.get('video_url') or request.form.get('url')
    
    if not url:
        return jsonify({"error": "Missing parameters"}), 400

    vid = extract_video_id(url)
    if not vid:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }

    try:
        # Step 1: ভিডিওর কী (Key) বের করা
        init_res = requests.post(
            "https://t-downloader.com/api/ajaxSearch",
            data={"q": f"https://www.youtube.com/watch?v={vid}", "vt": "home"},
            headers=headers,
            timeout=15
        ).json()

        title = init_res.get("title", "YouTube Video")
        links = init_res.get("links", {}).get("mp4", {})

        # কোয়ালিটি অনুযায়ী লিংক খোঁজা (720p / 360p / auto)
        k_val = None
        for q in ["720p", "360p", "auto"]:
            for item in links.values():
                if item.get("q") == q or item.get("f") == "mp4":
                    k_val = item.get("k")
                    break
            if k_val:
                break

        if not k_val:
            # প্রথম যেকোনো উপলব্ধ কী নেওয়া
            first_key = list(links.keys())[0]
            k_val = links[first_key].get("k")

        # Step 2: ডিরেক্ট MP4 ডাউনলোড লিংক তৈরি
        convert_res = requests.post(
            "https://t-downloader.com/api/ajaxConvert",
            data={"vid": vid, "k": k_val},
            headers=headers,
            timeout=15
        ).json()

        dlink = convert_res.get("dlink")

        if dlink:
            return jsonify({
                "status": "success",
                "url": dlink,
                "title": title
            })
        else:
            return jsonify({"error": "Could not generate download link"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
