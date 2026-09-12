import time
import threading
from flask import Flask, jsonify
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from supabase import create_client, Client

app = Flask(__name__)

# Supabase Credentials (আপনার প্রজেক্টের সঠিক URL ও Key)
SUPABASE_URL = "https://safymsagxrjymhfdzkph.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_qthdZZg-tjDRc_loLbVUYg_b77rK-Bv"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# ড্রাইভ লিংকগুলোর মেসেজ টেমপ্লেট
MESSAGE_TEMPLATE = """অভিনন্দন! আপনার পেমেন্ট সফল হয়েছে। আপনার প্রিমিয়াম মেগা বান্ডেল ও রিসোর্সের লিংকগুলো নিচে দেওয়া হলো:

🔥 CapCut Pro APK: https://drive.google.com/file/d/1k6lN0aaPvTRCqfmZT2kyY8zeRNRiXqDw/view?usp=drivesdk
🎓 ফেসবুক মনিটাইজেশন ও ভিডিও এডিটিং কোর্স: https://drive.google.com/drive/folders/1X5QrLG4vd1b2Ot2_cW2zkBSZ_I6y3y-k
🎬 ১.৫ লক্ষ মিক্সড মেগা রিলস বান্ডেল: https://drive.google.com/file/d/1tNWjaTjbnFMSarK_5yb3TqEzsg75m2QR/view?usp=drivesdk
🍿 বলিউড ও হলিউড মুভি ক্লিপস: https://drive.google.com/drive/folders/1Nms2_o8rjU-XCGPIOBdR94UhFVvMf9i4
🕌 ইসলামিক ভাইরাল রিলস প্যাক: https://drive.google.com/drive/folders/18k-dHfre5uBW9IU4iACChgHj_v8Vb4LU
🚀 ৩০,০০০ মাস্টারপিস ভিডিও প্যাক: https://drive.google.com/drive/folders/1t3mYGqEQ861WXNwZuywNa_X5hp16QJKN
🍔 AI ফুড ও হেলথ ভিডিও কালেকশন: https://drive.google.com/drive/folders/115kwC6eGj9YzmU4nQYHi9pKUMYSKx8wB

ধন্যবাদ Technography এর সাথে থাকার জন্য!"""

def send_whatsapp_message(phone, message):
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = uc.Chrome(options=options)
    try:
        # হোয়াটসঅ্যাপ ওয়েব ওপেন করা (প্রথমবার রান করলে টার্মিনালে কিউআর কোড স্ক্যান করে লগইন করতে হবে)
        driver.get("https://web.whatsapp.com")
        time.sleep(15) # পেজ লোড ও কিউআর কোড স্ক্যানের সময়

        # কাস্টমারের চ্যাট সরাসরি ওপেন করার লিংক
        formatted_phone = phone.replace("+", "").strip()
        if not formatted_phone.startswith("88"):
            formatted_phone = "88" + formatted_phone
            
        chat_url = f"https://web.whatsapp.com/send?phone={formatted_phone}&text={message}"
        driver.get(chat_url)
        
        time.sleep(10)
        
        # সেন্ড বাটনে ক্লিক করা
        send_btn_xpath = '//span[@data-icon="send"]'
        wait = WebDriverWait(driver, 20)
        send_button = wait.until(EC.element_to_be_clickable((By.XPATH, send_btn_xpath)))
        send_button.click()
        
        time.sleep(5)
        print(f"Successfully sent message to {phone}")
    except Exception as e:
        print(f"Error sending message to {phone}: {e}")
    finally:
        driver.quit()

def background_order_checker():
    """ব্যাকগ্রাউন্ডে সবসময় payments টেবিল চেক করবে"""
    while True:
        try:
            # payments টেবিল থেকে এমন এন্ট্রি খুঁজবে যেখানে is_used = TRUE কিন্তু whatsapp_number দেওয়া আছে
            response = supabase.table("payments").select("*").eq("is_used", True).not_.is_("whatsapp_number", "null").execute()
            orders = response.data
            
            if orders:
                for order in orders:
                    phone = order.get("whatsapp_number")
                    order_id = order.get("id")
                    
                    if phone:
                        print(f"Processing order for phone: {phone}")
                        send_whatsapp_message(phone, MESSAGE_TEMPLATE)
                        
                        # মেসেজ পাঠানো শেষ হলে whatsapp_number ফাকা করে দেওয়া যাতে ডাবল সেন্ড না হয়
                        supabase.table("payments").update({"whatsapp_number": None}).eq("id", order_id).execute()
                        
        except Exception as ex:
            print(f"Background worker error: {ex}")
            
        time.sleep(30) # প্রতি ৩০ সেকেন্ড পর পর চেক করবে

@app.route('/ping')
def ping():
    return jsonify({"status": "alive", "message": "Render is awake!"}), 200

@app.route('/')
def home():
    return "WhatsApp Automation Bot is Running!", 200

if __name__ == '__main__':
    # ব্যাকগ্রাউন্ড থ্রেড স্টার্ট করা
    t = threading.Thread(target=background_order_checker, daemon=True)
    t.start()
    
    # Flask অ্যাপ রান করা
    app.run(host='0.0.0.0', port=5000)
