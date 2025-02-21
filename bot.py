import json
import os
import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler

# 🔹 Cargar variables de entorno
load_dotenv()

# 🔹 Configuración de Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_json = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, SCOPE)
client = gspread.authorize(creds)

# 📝 Hoja de cálculo
SHEET_NAME = "14-MFH08mqKa0cTJLVIHtd724FasnnOORN7R14WPwS_s"
sheet = client.open_by_key(SHEET_NAME).sheet1

# 🔹 Estados del flujo de conversación
(
    NOMBRE, EDAD, CIUDAD, REDES, REDES_CONFIRM, RED_PRINCIPAL, USUARIO, SEGUIDORES, 
    DINERO, TIEMPO, FOTO, VIDEO, EMAIL, FINAL
) = range(14)

async def start(update: Update, context: CallbackContext) -> int:
    keyboard = [["🚀 Empezar"]]
    await update.message.reply_text(
        "¡Bienvenida! Empecemos con algunas preguntas para conocerte mejor.",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return NOMBRE

async def nombre(update: Update, context: CallbackContext) -> int:
    context.user_data['nombre'] = update.message.text
    await update.message.reply_text("¿Cuántos años tienes?", reply_markup=ReplyKeyboardRemove())
    return EDAD

async def edad(update: Update, context: CallbackContext) -> int:
    try:
        edad = int(update.message.text)
        if edad < 18:
            await update.message.reply_text("Debes ser mayor de 18 años para continuar.")
            return ConversationHandler.END
        context.user_data['edad'] = edad
        await update.message.reply_text("¿En qué ciudad y país vives?")
        return CIUDAD
    except ValueError:
        await update.message.reply_text("Por favor, ingresa una edad válida.")
        return EDAD

async def ciudad(update: Update, context: CallbackContext) -> int:
    context.user_data['ciudad'] = update.message.text
    keyboard = [
        ["📸 Instagram", "🎥 TikTok", "🐦 Twitter"],
        ["📢 Telegram", "🔗 Facebook", "💬 Reddit"],
        ["✅ Listo"]
    ]
    context.user_data['redes'] = []
    await update.message.reply_text(
        "¿Qué redes sociales usas? Selecciona todas las que apliquen y pulsa '✅ Listo' cuando termines.",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
    )
    return REDES

async def redes(update: Update, context: CallbackContext) -> int:
    selected_option = update.message.text

    if selected_option == "✅ Listo":
        if not context.user_data['redes']:
            await update.message.reply_text("Debes seleccionar al menos una red social.")
            return REDES
        await update.message.reply_text("¿En qué red social te sientes más cómoda o eres más activa?")
        return RED_PRINCIPAL
    else:
        if selected_option not in context.user_data['redes']:
            context.user_data['redes'].append(selected_option)
        return REDES

async def red_principal(update: Update, context: CallbackContext) -> int:
    context.user_data['red_principal'] = update.message.text
    await update.message.reply_text("¿Cuál es tu usuario en esa red? (@nombre)")
    return USUARIO

async def usuario(update: Update, context: CallbackContext) -> int:
    context.user_data['usuario'] = update.message.text
    keyboard = [["Menos de 1,000", "1,000 - 5,000"], ["5,000 - 10,000", "Más de 10,000"]]
    await update.message.reply_text("¿Cuántos seguidores tienes en esa red?", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return SEGUIDORES

async def seguidores(update: Update, context: CallbackContext) -> int:
    context.user_data['seguidores'] = update.message.text
    await update.message.reply_text("Por favor, envíame una foto tuya (posado natural).")
    return FOTO

async def foto(update: Update, context: CallbackContext) -> int:
    if update.message.photo:
        photo_file = update.message.photo[-1].file_id
        context.user_data['foto'] = photo_file
        await update.message.reply_text("Ahora envíame un video corto presentándote.")
        return VIDEO
    else:
        await update.message.reply_text("Por favor, envía una foto válida.")
        return FOTO

async def video(update: Update, context: CallbackContext) -> int:
    if update.message.video:
        video_file = update.message.video.file_id
        context.user_data['video'] = video_file
        await update.message.reply_text("Por último, ¿cuál es tu correo electrónico?")
        return EMAIL
    else:
        await update.message.reply_text("Por favor, envía un video válido.")
        return VIDEO

async def email(update: Update, context: CallbackContext) -> int:
    email = update.message.text
    if "@" not in email or "." not in email:
        await update.message.reply_text("Por favor, ingresa un email válido.")
        return EMAIL

    context.user_data['email'] = email
    await guardar_en_sheets(update, context)
    await update.message.reply_text("✅ Registro completado. ¡Gracias!")
    return FINAL

async def guardar_en_sheets(update: Update, context: CallbackContext):
    usuario_id = update.message.chat.id
    datos = [
        usuario_id,
        context.user_data.get('nombre', ''),
        context.user_data.get('edad', ''),
        context.user_data.get('ciudad', ''),
        ", ".join(context.user_data.get('redes', [])),
        context.user_data.get('red_principal', ''),
        context.user_data.get('usuario', ''),
        context.user_data.get('seguidores', ''),
        context.user_data.get('foto', ''),
        context.user_data.get('video', ''),
        context.user_data.get('email', '')
    ]
    try:
        sheet.append_row(datos)
        await update.message.reply_text("✅ Tus datos han sido guardados correctamente.")
    except Exception as e:
        await update.message.reply_text(f"⚠ Hubo un error al guardar tus datos: {e}")

# 🔹 Configuración del bot
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

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
        RED_PRINCIPAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, red_principal)],
        USUARIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, usuario)],
        SEGUIDORES: [MessageHandler(filters.TEXT & ~filters.COMMAND, seguidores)],
        FOTO: [MessageHandler(filters.PHOTO, foto)],
        VIDEO: [MessageHandler(filters.VIDEO, video)],
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)]
    },
    fallbacks=[]
)

application.add_handler(conv_handler)

if __name__ == "__main__":
    application.run_polling()
