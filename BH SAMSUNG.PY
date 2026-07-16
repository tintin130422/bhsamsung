import telebot
import re
from PIL import Image
import pytesseract
import io
import traceback

bot = telebot.TeleBot("8715678326:AAGEermOBKQsos4-f1rSNIjlVuhLFvhwk8E")
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_imeis(text):
    return re.findall(r'\b\d{15}\b', text)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Bot đang test... Gửi ảnh đi")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "📸 Đang xử lý ảnh...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        img = Image.open(io.BytesIO(downloaded))
        text = pytesseract.image_to_string(img, lang='eng')
        
        imeis = extract_imeis(text)
        
        if imeis:
            bot.reply_to(message, f"✅ Tìm thấy IMEI: {imeis}")
        else:
            bot.reply_to(message, "❌ Không tìm thấy IMEI nào.")
            
    except Exception as e:
        error_msg = traceback.format_exc()
        bot.reply_to(message, f"❌ Lỗi: {str(e)}\n\n{error_msg[:500]}")

print("Bot debug đang chạy...")
bot.infinity_polling()