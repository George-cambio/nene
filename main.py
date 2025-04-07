import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import requests

# Carga de variables desde el entorno
BOT_TOKEN = os.getenv("7749659951:AAEI_QjqnGWlo6_K7yf9f6K0NIGtva_92sU")
ZMO_API_KEY = os.getenv("eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiI5ZTI1NjU0ZDYwYzY0MDhlYjE1NGQ2ZjhjZGM5Yjg1NSIsImF1dGhLZXkiOiJTVEFOREFSRF9VU0VSLEdST1VQX0FETUlOLFNZU19BRE1JTiIsImdyb3VwSWQiOiJhYmUyNzIwYjBhYTU0ZTFjOWVlNGQ0MzNkNTc0NjYzYiIsImV4cCI6MTY4OTc1NjczMn0.LnsMwrH_Bvz17e_dj_BLYwcKRLesCoXHm72x16-kqHtnoYKU4cVwYITJf4DQvSEaq5XV_ksa4WjZ1LntU2gT")

# Verificación
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN no está definido en las variables de entorno.")

if not ZMO_API_KEY:
    raise ValueError("ZMO_API_KEY no está definido en las variables de entorno.")

# Variables para almacenar temporalmente imágenes
user_images = {}

# Función de bienvenida
def start(update, context):
    update.message.reply_text("¡Hola! Soy tu bot con ZMO.AI 🤖\nEnvíame primero la imagen original y luego la imagen del rostro para hacer el face swap.")

# Función para manejar imágenes
def handle_image(update, context):
    user_id = update.message.from_user.id
    photo_file = update.message.photo[-1].get_file()
    image_url = photo_file.file_path

    if user_id not in user_images:
        user_images[user_id] = {"original": image_url, "face": None}
        update.message.reply_text("Imagen original recibida ✅. Ahora envíame la imagen del rostro que quieres usar para el swap.")
    elif not user_images[user_id]["face"]:
        user_images[user_id]["face"] = image_url
        update.message.reply_text("Imagen del rostro recibida ✅. Procesando... 🔄")

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
                update.message.reply_text("✅ Swap completado")
                update.message.reply_photo(result["resultUrl"])
            else:
                update.message.reply_text("⚠️ No se pudo realizar el swap. Intenta con otras imágenes.")

        except Exception as e:
            update.message.reply_text(f"Ocurrió un error: {str(e)}")

        # Reiniciar imágenes del usuario
        user_images[user_id] = {"original": None, "face": None}
    else:
        update.message.reply_text("Ya recibí dos imágenes. Si deseas hacer otro swap, envíame una nueva imagen original.")

# Configuración del bot
updater = Updater(BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.photo, handle_image))

# Arranque del bot
updater.start_polling()
print("Bot corriendo...")
updater.idle()
