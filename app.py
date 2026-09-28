import os
import threading
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN")


def download_and_send(chat_id, video_url):
  try:
    # Cobalt API ব্যবহার করে সরাসরি ভিডিও ফাইল লিংক নেওয়া (কোনো আইপি ব্লক খাবে না)
    api_url = "https://api.cobalt.tools/api/json"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {"url": video_url, "vQuality": "720"}

    res = requests.post(api_url, json=payload, headers=headers, timeout=20)
    data = res.json()

    stream_url = data.get("url")
    if not stream_url:
      raise Exception("ভিডিও লিংক তৈরি করা যায়নি।")

    # সরাসরি টেলিগ্রাম চ্যাটে ভিডিও পাঠানো
    tg_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    tg_res = requests.post(
        tg_url,
        data={
            "chat_id": chat_id,
            "video": stream_url,
            "caption": "▶️ <b>ভিডিও ডাউনলোড সম্পন্ন!</b>",
            "parse_mode": "HTML",
        },
        timeout=60,
    )

    if not tg_res.json().get("ok"):
      raise Exception(tg_res.json().get("description"))

  except Exception as e:
    err_api = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(
        err_api,
        json={
            "chat_id": chat_id,
            "text": f"❌ ডাউনলোড ব্যর্থ: {str(e)}",
            "parse_mode": "HTML",
        },
    )


@app.route("/download", methods=["POST"])
def handle_download():
  data = request.json or {}
  chat_id = data.get("chat_id")
  video_url = data.get("url")

  if not chat_id or not video_url:
    return jsonify({"error": "Missing parameters"}), 400

  threading.Thread(target=download_and_send, args=(chat_id, video_url)).start()
  return jsonify({"status": "processing"})


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
