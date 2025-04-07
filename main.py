import os
import logging
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)

# Carga de variables desde el entorno
BOT_TOKEN = os.getenv("7749659951:AAEI_QjqnGWlo6_K7yf9f6K0NIGtva_92sU")
ZMO_API_KEY = os.getenv("eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiI5ZTI1NjU0ZDYwYzY0MDhlYjE1NGQ2ZjhjZGM5Yjg1NSIsImF1dGhLZXkiOiJTVEFOREFSRF9VU0VSLEdST1VQX0FETUlOLFNZU19BRE1JTiIsImdyb3VwSWQiOiJhYmUyNzIwYjBhYTU0ZTFjOWVlNGQ0MzNkNTc0NjYzYiIsImV4cCI6MTY4OTc1NjczMn0.LnsMwrH_Bvz17e_dj_BLYwcKRLesCoXHm72x16-kqHtnoYKU4cVwYITJf4DQvSEaq5XV_ksa4WjZ1LntU2gT")

# Verificación
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN no está definido en las variables de entorno.")
if not ZMO_API_KEY:
    raise ValueError("ZMO_API_KEY no está definido en las variables de entorno.")

# Configuración del log
logging.basicConfig(level=logging.INFO)

# Almacenamiento temporal por usuario
user_images = {}

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Envíame primero la imagen original y luego la del rostro para hacer el swap.")

# Manejo de imágenes
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    photo_file = await update.message.photo[-1].get_file()
    image_url = photo_file.file_path

    if user_id not in user_images:
        user_images[user_id] = {"original": image_url, "face": None}
        await update.message.reply_text("✅ Imagen original recibida. Ahora envíame la imagen del rostro.")
    elif not user_images[user_id]["face"]:
        user_images[user_id]["face"] = image_url
        await update.message.reply_text("🧠 Procesando el face swap...")

        headers = {
            "Content-Type": "application/json",
            "accessKey": ZMO_API_KEY
        }

        data = {
            "originalImgUrl": user_images[user_id]["original"],
            "targetImgUrl": user_images[user_id]["face"]
        }

        try:
            response = requests.post("https://open-api.zmo.ai/open/swap/anything/genSegImg",
                                     headers=headers, json=data)
            result = response.json()

            if "resultUrl" in result:
                await update.message.reply_photo(result["resultUrl"])
            else:
                await update.message.reply_text("⚠️ No se pudo hacer el swap. Intenta con otras imágenes.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

        # Reiniciar datos del usuario
        user_images[user_id] = {"original": None, "face": None}
    else:
        await update.message.reply_text("Ya tengo dos imágenes. Si quieres repetir, envíame una nueva imagen original.")

# Main
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    print("🤖 Bot corriendo...")
    app.run_polling()
