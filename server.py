import os
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

app = Flask(__name__)

# Read from .env
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Telegram API base
BASE_TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


@app.route("/", methods=["GET"])
def index():
    return {"message": "Backend running"}, 200

@app.route("/api/health", methods=["GET"])
def health():
    return {"status": "ok"}, 200


@app.route("/send-to-telegram", methods=["POST"])
def send_to_telegram():
    try:
        # Accept both form-data and raw JSON
        data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})

        # Debug: log incoming form data
        app.logger.info(f"Incoming form data: {data}")
        app.logger.info(f"Incoming files: {list(request.files.keys())}")

        # Build the formatted message
        message = (
            "🔧 *New Service Request*\n\n"
            f"👤 *Name*: {data.get('name', '')}\n"
            f"📞 *Contact*: {data.get('contact', '')}\n"
            f"💻 *Unit*: {data.get('unit', '')}\n"
            f"📏 *Inches*: {data.get('inches', '')}\n"
            f"🏷️ *Brand*: {data.get('brand', '')}\n"
            f"📍 *Address*: {data.get('address', '')}\n"
            f"⚠️ *Issue*: {data.get('issue', '')}\n"
            f"📝 *Desc*: {data.get('issue_desc', '')}"
        )

        # ✅ Handle photo upload
        if "photo" in request.files:
            photo = request.files["photo"]
            app.logger.info(f"Photo received: filename={photo.filename}, mimetype={photo.mimetype}")

            send_photo_url = f"{BASE_TELEGRAM_URL}/sendPhoto"
            photo_resp = requests.post(
                send_photo_url,
                data={
                    "chat_id": CHAT_ID,
                    "caption": message,
                    "parse_mode": "Markdown"
                },
                files={"photo": (photo.filename, photo.stream, photo.mimetype)}
            )

            app.logger.info(f"Telegram sendPhoto response: {photo_resp.text}")

            return jsonify({
                "success": True,
                "message": "Photo + caption sent to Telegram",
                "telegram_response": photo_resp.json()
            }), 200

        # ✅ Fallback: send as text only
        send_msg_url = f"{BASE_TELEGRAM_URL}/sendMessage"
        msg_resp = requests.post(send_msg_url, json={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        })

        app.logger.info(f"Telegram sendMessage response: {msg_resp.text}")

        return jsonify({
            "success": True,
            "message": "Message sent to Telegram",
            "telegram_response": msg_resp.json()
        }), 200

    except Exception as e:
        app.logger.error(f"Error in send_to_telegram: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/echo", methods=["POST"])
def echo():
    data = request.get_json(silent=True) or {}
    return jsonify({"you_sent": data}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
