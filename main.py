import os
import logging
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()
TELEGRAM_TOKEN = os.getenv("7749659951:AAEI_QjqnGWlo6_K7yf9f6K0NIGtva_92sU")
ZMO_API_KEY = os.getenv("eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiI5ZTI1NjU0ZDYwYzY0MDhlYjE1NGQ2ZjhjZGM5Yjg1NSIsImF1dGhLZXkiOiJTVEFOREFSRF9VU0VSLEdST1VQX0FETUlOLFNZU19BRE1JTiIsImdyb3VwSWQiOiJhYmUyNzIwYjBhYTU0ZTFjOWVlNGQ0MzNkNTc0NjYzYiIsImV4cCI6MTY4OTc1NjczMn0.LnsMwrH_Bvz17e_dj_BLYwcKRLesCoXHm72x16-kqHtnoYKU4cVwYITJf4DQvSEaq5XV_ksa4WjZ1LntU2gT")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola 👋 Enviame un link a una imagen y haré face swap con ZMO.AI ✨")

def zmo_faceswap(image_url):
    url = "https://open-api.zmo.ai/open/swap/anything/genSegImg"
    headers = {
        "Content-Type": "application/json",
        "accessKey": ZMO_API_KEY
    }
    data = {
        "originalImgUrl": image_url
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            return result["message"]["hqPreview"]
    return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.startswith("http"):
        await update.message.reply_text("Procesando tu imagen... 🔄")
        result = zmo_faceswap(text)
        if result:
            await update.message.reply_photo(photo=result, caption="Aquí tienes tu imagen con face swap 🤖")
        else:
            await update.message.reply_text("❌ Hubo un error procesando la imagen.")
    else:
        await update.message.reply_text("Por favor, envíame un enlace de imagen válido (empezando con http).")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
