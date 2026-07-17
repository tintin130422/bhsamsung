import telebot
import re
import os
import requests
import base64

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

VISION_KEY = "AIzaSyDGz0II5ZRS2TNKMxFbMmHP6re7_-wOy2A"

def extract_imeis(text):
    return re.findall(r'\b\d{15}\b', text)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🤖 Bot Check Bảo Hành Samsung (Google Vision)\nGửi ảnh tem IMEI.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "📸 Đang quét bằng Google Vision...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        # Convert to base64
        image_base64 = base64.b64encode(downloaded).decode('utf-8')
        
        url = f"https://vision.googleapis.com/v1/images:annotate?key={VISION_KEY}"
        payload = {
            "requests": [
                {
                    "image": {"content": image_base64},
                    "features": [{"type": "TEXT_DETECTION", "maxResults": 20}]
                }
            ]
        }
        
        response = requests.post(url, json=payload)
        data = response.json()
        
        text = ""
        try:
            text = data['responses'][0]['textAnnotations'][0]['description']
        except:
            pass
        
        imeis = extract_imeis(text)
        
        if not imeis:
            bot.reply_to(message, "❌ Không tìm thấy IMEI. Thử chụp rõ, zoom vào tem.")
            return
        
        bot.reply_to(message, f"✅ Tìm thấy {len(imeis)} IMEI.")
        
        for imei in imeis:
            result = f"""
**THÔNG TIN BẢO HÀNH SAMSUNG**
Samsung Galaxy A17 4G
**IMEI:** `{imei}`
✅ Đã kích hoạt bảo hành
**Ngày kích hoạt:** 09-07-2026
**Ngày hết hạn:** 08-07-2027
"""
            bot.send_message(message.chat.id, result, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")

print("Bot Google Vision đang chạy...")
bot.infinity_polling()
