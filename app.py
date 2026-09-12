import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# মেটা থেকে পাওয়া আপনার ক্রেডেনশিয়ালস
TOKEN = os.getenv("WHATSAPP_TOKEN", "EAAOibJc4tZAwBSQ1qVin0onZCjscUTHypCVjIxHvBPEEp46HJh3g5KQKN2ZB39zsF7REXsgk1cPDlLExgYJEHU0ORYZBkjZCTIGa6AbfB28DAOqNLumbZCzcqkEs2wWzeZBqr59ZAZCek8EqHISzAkHuzDJRmhFL90DYZB0a6mn4Ekyg9QpxkA35ZANuwMdfKqmyQZDZD")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "1243931905479404")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "technography_verify_token")

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp Supabase Order Bot is running successfully!"

# হোয়াটসঅ্যাপ ওয়েবহুক ভেরিফিকেশন (যদি প্রয়োজন হয়)
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

# পেমেন্ট টেবিল বা ডেটাবেস থেকে ট্রিগার হয়ে হোয়াটসঅ্যাপে কনফার্মেশন পাঠানোর রাউট
@app.route("/send-confirmation", methods=["POST"])
def send_confirmation():
    data = request.json
    print("Received Data from Payment Table:", data)

    try:
        # পেমেন্ট টেবিল বা ডেটাবেস থেকে আসা কাস্টমার ডাটা
        customer_phone = data.get("phone")  # কাস্টমারের হোয়াটসঅ্যাপ নম্বর
        customer_name = data.get("name", "গ্রাহক")
        product_name = data.get("product", "ডিজিটাল প্রোডাক্ট")
        download_link = data.get("link", "https://yourwebsite.com/download")

        if not customer_phone:
            return jsonify({"status": "error", "message": "Phone number not found in data"}), 400

        # হোয়াটসঅ্যাপে পাঠানোর জন্য কনফার্মেশন মেসেজ তৈরি
        message_text = (
            f"ধন্যবাদ {customer_name}! পেমেন্ট সফলভাবে সম্পন্ন হয়েছে।\n\n"
            f"📦 প্রোডাক্ট: {product_name}\n"
            f"🔗 ডাউনলোডের লিংক: {download_link}\n\n"
            f"আপনার অর্ডারটি কনফার্ম করা হলো।"
        )

        # হোয়াটসঅ্যাপ এপিআই-এর মাধ্যমে মেসেজ পাঠানো
        response = send_whatsapp_message(PHONE_NUMBER_ID, customer_phone, message_text)

        return jsonify({"status": "success", "response": response}), 200

    except Exception as e:
        print("Error in sending confirmation:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

def send_whatsapp_message(phone_number_id, recipient_number, message_text):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_number,
        "type": "text",
        "text": {"body": message_text},
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
