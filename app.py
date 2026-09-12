import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# মেটা থেকে পাওয়া ক্রেডেনশিয়ালস
TOKEN = os.getenv("WHATSAPP_TOKEN", "EAAOibJc4tZAwBSQ1qVin0onZCjscUTHypCVjIxHvBPEEp46HJh3g5KQKN2ZB39zsF7REXsgk1cPDlLExgYJEHU0ORYZBkjZCTIGa6AbfB28DAOqNLumbZCzcqkEs2wWzeZBqr59ZAZCek8EqHISzAkHuzDJRmhFL90DYZB0a6mn4Ekyg9QpxkA35ZANuwMdfKqmyQZDZD")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "1243931905479404")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "technography_verify_token")

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp Bot is running successfully!"

# ১. মেটা থেকে আসা ওয়েবহুক ভেরিফাই করার জন্য (Webhook Verification)
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

# ২. কাস্টমারের মেসেজ রিসিভ করা এবং অটো রিপ্লাই পাঠানোর মেইন ফাংশন
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Received Data:", data)

    try:
        if "entry" in data:
            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    if "messages" in value:
                        phone_number_id = value["metadata"]["phone_number_id"]
                        message = value["messages"][0]
                        from_number = message["from"] # কাস্টমারের হোয়াটসঅ্যাপ নম্বর
                        msg_body = message["text"]["body"] # কাস্টমার কী লিখেছে

                        print(f"Message from {from_number}: {msg_body}")

                        # কাস্টমারকে কী উত্তর পাঠাবেন
                        reply_text = "স্বাগতম! আমাদের ডিজিটাল প্রোডাক্ট এবং সফটওয়্যার সম্পর্কে জানতে যোগাযোগ করার জন্য ধন্যবাদ। খুব শীঘ্রই আমাদের প্রতিনিধি আপনার সাথে কথা বলবে।"

                        # হোয়াটসঅ্যাপে মেসেজ পাঠানোর ফাংশন কল করা
                        send_whatsapp_message(phone_number_id, from_number, reply_text)

    except Exception as e:
        print("Error processing webhook:", e)

    return jsonify({"status": "success"}), 200

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
    print("Send Response:", response.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
