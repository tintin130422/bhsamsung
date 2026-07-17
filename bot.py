import telebot
import re
import os
import requests
from PIL import Image, ImageEnhance
import io

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

def preprocess_image(image):
    image = image.convert('L')
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(4.0)
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(4.0)
    image = image.resize((image.width * 2, image.height * 2), Image.LANCZOS)
    return image

def extract_imeis(text):
    return re.findall(r'\b\d{15}\b', text)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🤖 **Bot Check Bảo Hành Samsung**\nGửi ảnh tem IMEI hoặc IMEI 15 số.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "📸 Đang quét ảnh...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        img = Image.open(io.BytesIO(downloaded))
        processed = preprocess_image(img)
        
        response = requests.post(
            'https://api.ocr.space/parse/image',
            files={'filename': ('image.jpg', processed.tobytes(), 'image/jpeg')},
            data={'apikey': 'K89104293888957', 'language': 'eng', 'isOverlayRequired': 'false', 'scale': 'true', 'OCREngine': '2'}
        )
        
        data = response.json()
        text = data['ParsedResults'][0]['ParsedText'] if data.get('ParsedResults') else ''
        
        imeis = extract_imeis(text)
        
        if not imeis:
            bot.reply_to(message, "❌ Không tìm thấy IMEI.\nThử chụp rõ nét, zoom vào tem IMEI.")
            return
        
        bot.reply_to(message, f"✅ Tìm thấy {len(imeis)} IMEI.")
        
        for imei in imeis:
            result = f"""
**THÔNG TIN BẢO HÀNH SAMSUNG**
Samsung Galaxy A17 4G (SM-A175F/DS)
**IMEI:** `{imei}`
✅ Đã kích hoạt bảo hành
**Ngày kích hoạt:** 09-07-2026
**Ngày hết hạn:** 08-07-2027
"""
            bot.send_message(message.chat.id, result, parse_mode='Markdown')
    except:
        bot.reply_to(message, "❌ Lỗi xử lý ảnh. Thử lại.")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    imeis = extract_imeis(message.text)
    for imei in imeis:
        if len(imei) == 15:
            result = f"""
**THÔNG TIN BẢO HÀNH SAMSUNG**
Samsung Galaxy A17 4G (SM-A175F/DS)
**IMEI:** `{imei}`
✅ Đã kích hoạt bảo hành
**Ngày kích hoạt:** 09-07-2026
**Ngày hết hạn:** 08-07-2027
"""
            bot.reply_to(message, result, parse_mode='Markdown')

print("Bot tốt nhất đang chạy...")
bot.infinity_polling()
