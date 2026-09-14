import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # CORS এনাবল করা হলো যাতে ওয়েবসাইট থেকে রিকোয়েস্ট ব্লক না হয়

# মেটা থেকে পাওয়া আপনার ক্রেডেনশিয়ালস
TOKEN = os.getenv("WHATSAPP_TOKEN", "আপনার_স্থায়ী_টোকেনটি_এখানে_বসান")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "1243931905479404")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "technography_verify_token")

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp Supabase Order Bot is running successfully!"

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification failed", 403
    return "Hello World", 200

@app.route("/send-confirmation", methods=["POST", "OPTIONS"])
def send_confirmation():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.json
    print("Received Data from Website:", data)

    try:
        customer_phone = data.get("phone")
        customer_name = data.get("name", "গ্রাহক")
        download_link = data.get("link", "https://technographybd.xyz/mega-bundle-vip-access.html")

        if not customer_phone:
            return jsonify({"status": "error", "message": "Phone number not found in data"}), 400

        # মেটার অনুমোদিত টেমপ্লেট দিয়ে মেসেজ পাঠানো
        response = send_whatsapp_template(PHONE_NUMBER_ID, customer_phone, customer_name, download_link)
        print("WhatsApp API Response:", response)

        return jsonify({"status": "success", "response": response}), 200

    except Exception as e:
        print("Error in sending confirmation:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

def send_whatsapp_template(phone_number_id, recipient_number, customer_name, download_link):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    
    # মেটা টেমপ্লেট পে-লোড (যা আপনার তৈরি করা order_delivery টেমপ্লেটকে কল করবে)
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_number,
        "type": "template",
        "template": {
            "name": "order_delivery",  # মেটাতে তৈরি করা টেমপ্লেটের নাম
            "language": {
                "code": "bn"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": customer_name},  # {{1}} এর জায়গায় বসবে
                        {"type": "text", "text": download_link}   # {{2}} এর জায়গায় বসবে
                    ]
                }
            ]
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
