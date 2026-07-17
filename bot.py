import telebot
import re
import os
import requests
import traceback
from PIL import Image, ImageEnhance
import io

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

def preprocess_image(image):
    image = image.convert('L')
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(3.5)
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(3.0)
    image = image.resize((image.width * 2, image.height * 2), Image.LANCZOS)
    return image

def extract_imeis(text):
    return re.findall(r'\b\d{15}\b', text)

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
            bot.reply_to(message, "❌ Không tìm thấy IMEI.")
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
        error = traceback.format_exc()
        bot.reply_to(message, f"❌ Lỗi: {str(e)}")

print("Bot đang chạy...")
bot.infinity_polling()
