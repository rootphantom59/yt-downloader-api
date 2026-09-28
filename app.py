import os
import threading
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN")


def process_video(chat_id, video_url):
  try:
    # ইউটিউবের আইপি ব্লকিং বাইপাস করার API
    api_url = "https://api.cobalt.tools/api/json"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {"url": video_url, "vQuality": "720"}

    r = requests.post(api_url, json=payload, headers=headers, timeout=25)
    result = r.json()

    media_link = result.get("url")
    if not media_link:
      raise Exception("ভিডিও লিংক সংগ্রহ করা যায়নি।")

    # সরাসরি টেলিগ্রামে ভিডিও পুশ করা
    tg_endpoint = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    tg_res = requests.post(
        tg_endpoint,
        data={
            "chat_id": chat_id,
            "video": media_link,
            "caption": "▶️ <b>ভিডিও ডাউনলোড সম্পন্ন!</b>",
            "parse_mode": "HTML",
        },
        timeout=60,
    )

    if not tg_res.json().get("ok"):
      raise Exception(tg_res.json().get("description"))

  except Exception as err:
    # কোনো সমস্যা হলে টেলিগ্রামে ইউজারকে মেসেজ পাঠানো
    err_endpoint = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(
        err_endpoint,
        json={
            "chat_id": chat_id,
            "text": f"❌ ত্রুটি: {str(err)}",
            "parse_mode": "HTML",
        },
    )


@app.route("/download", methods=["POST"])
def download():
  data = request.get_json(silent=True) or request.form.to_dict() or {}
  chat_id = data.get("chat_id")
  video_url = data.get("url")

  if not chat_id or not video_url:
    return jsonify({"error": "Missing parameters"}), 400

  threading.Thread(target=process_video, args=(chat_id, video_url)).start()
  return jsonify({"status": "processing"})


@app.route("/")
def home():
  return "Server is Running!"


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
