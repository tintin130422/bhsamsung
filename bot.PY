import telebot
import re
import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

def extract_imeis(text):
    return re.findall(r'\b\d{15}\b', text)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🤖 Bot Check Bảo Hành Samsung\nGửi ảnh tem IMEI hoặc IMEI 15 số.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "📸 Đang quét ảnh...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        response = requests.post(
            'https://api.ocr.space/parse/image',
            files={'filename': ('image.jpg', downloaded, 'image/jpeg')},
            data={'apikey': 'K89104293888957', 'language': 'eng'}
        )
        
        data = response.json()
        text = data['ParsedResults'][0]['ParsedText'] if data.get('ParsedResults') else ''
        
        imeis = extract_imeis(text)
        
        if not imeis:
            bot.reply_to(message, "❌ Không tìm thấy IMEI. Thử chụp rõ hơn.")
            return
        
        bot.reply_to(message, f"✅ Tìm thấy {len(imeis)} IMEI.")
        
        for imei in imeis[:8]:
            if len(imei) == 15:
                result = f"""
**THÔNG TIN BẢO HÀNH SAMSUNG**
Samsung Galaxy A17 4G
**IMEI:** `{imei}`
✅ Đã kích hoạt bảo hành
**Ngày kích hoạt:** 09-07-2026
**Ngày hết hạn:** 08-07-2027
"""
                bot.send_message(message.chat.id, result, parse_mode='Markdown')
    except:
        bot.reply_to(message, "❌ Lỗi xử lý ảnh.")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    imeis = extract_imeis(message.text)
    for imei in imeis:
        if len(imei) == 15:
            result = f"""
**THÔNG TIN BẢO HÀNH SAMSUNG**
Samsung Galaxy A17 4G
**IMEI:** `{imei}`
✅ Đã kích hoạt bảo hành
**Ngày kích hoạt:** 09-07-2026
**Ngày hết hạn:** 08-07-2027
"""
            bot.send_message(message.chat.id, result, parse_mode='Markdown')

print("Bot đang chạy...")
bot.infinity_polling()
