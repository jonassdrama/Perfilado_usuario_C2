import json
import os
import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler

# 🔹 Cargar variables de entorno
load_dotenv()  # Carga las variables desde un archivo .env

# 🔹 Configuración de Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Cargar credenciales desde archivo JSON (más seguro que usar variables de entorno)
with open("credentials.json", "r") as f:
    creds_json = json.load(f)

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, SCOPE)
client = gspread.authorize(creds)

# 📝 Cambia aquí el nombre de la hoja de cálculo
SHEET_NAME = "14-MFH08mqKa0cTJLVIHtd724FasnnOORN7R14WPwS_s"
sheet = client.open_by_key(SHEET_NAME).sheet1

# 🔹 Estados del flujo de conversación
NOMBRE, EDAD, CIUDAD, REDES, EMAIL = range(5)

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("¡Bienvenida! Empecemos con algunas preguntas para conocerte mejor.\n¿Cuál es tu nombre o apodo?")
    return NOMBRE

def nombre(update: Update, context: CallbackContext) -> int:
    context.user_data['nombre'] = update.message.text
    update.message.reply_text("¿Cuántos años tienes?")
    return EDAD

def edad(update: Update, context: CallbackContext) -> int:
    try:
        edad = int(update.message.text)
        if edad < 18:
            update.message.reply_text("Debes ser mayor de 18 años para continuar.")
            return ConversationHandler.END
        context.user_data['edad'] = edad
        update.message.reply_text("¿En qué ciudad y país vives?")
        return CIUDAD
    except ValueError:
        update.message.reply_text("Por favor, ingresa una edad válida en números.")
        return EDAD

def ciudad(update: Update, context: CallbackContext) -> int:
    context.user_data['ciudad'] = update.message.text
    keyboard = [["Instagram", "TikTok", "Twitter"], ["Telegram", "Facebook", "Reddit"], ["No uso redes, pero quiero aprender"]]
    update.message.reply_text(
        "¿Qué redes sociales usas? (Elige una o más, escribe las que uses)",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return REDES

def redes(update: Update, context: CallbackContext) -> int:
    context.user_data['redes'] = update.message.text
    update.message.reply_text("Por último, ¿cuál es tu correo electrónico?")
    return EMAIL

def email(update: Update, context: CallbackContext) -> int:
    email = update.message.text
    if "@" not in email or "." not in email:
        update.message.reply_text("Por favor, ingresa un email válido.")
        return EMAIL

    context.user_data['email'] = email
    guardar_en_sheets(update, context)
    update.message.reply_text("✅ Registro completado. ¡Gracias!")
    return ConversationHandler.END

def guardar_en_sheets(update: Update, context: CallbackContext):
    usuario_id = update.message.chat.id
    datos = [
        usuario_id,
        context.user_data.get('nombre', ''),
        context.user_data.get('edad', ''),
        context.user_data.get('ciudad', ''),
        context.user_data.get('redes', ''),
        context.user_data.get('email', '')
    ]
    try:
        sheet.append_row(datos)
        update.message.reply_text("✅ Tus datos han sido guardados correctamente.")
    except Exception as e:
        update.message.reply_text(f"⚠ Hubo un error al guardar tus datos: {e}")

# 🔹 Configuración del bot de Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # O reemplázalo con tu token directamente

if not TELEGRAM_TOKEN:
    raise ValueError("⚠ ERROR: No se encontró TELEGRAM_TOKEN. Verifica tu configuración.")

application = Application.builder().token(TELEGRAM_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, nombre)],
        EDAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, edad)],
        CIUDAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, ciudad)],
        REDES: [MessageHandler(filters.TEXT & ~filters.COMMAND, redes)],
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)],
    },
    fallbacks=[]
)

application.add_handler(conv_handler)
application.run_polling()
