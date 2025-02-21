import json
import os
import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, ReplyKeyboardMarkup
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
    NOMBRE, EDAD, CIUDAD, REDES, RED_PRINCIPAL, USUARIO, SEGUIDORES,
    DINERO, TIEMPO, VENTAS, COMUNICACION, CREATIVIDAD, APARICION, CONTENIDO, EMAIL, FINAL
) = range(15)

async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("¡Bienvenida! Empecemos con algunas preguntas para conocerte mejor.\n¿Cuál es tu nombre o apodo?")
    return NOMBRE

async def nombre(update: Update, context: CallbackContext) -> int:
    context.user_data['nombre'] = update.message.text
    await update.message.reply_text("¿Cuántos años tienes?")
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
    keyboard = [["✅ Sí, ya tengo una fuente de ingresos"], ["⭕ No, pero me gustaría empezar"]]
    await update.message.reply_text("¿Actualmente ganas dinero online?", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return DINERO

async def dinero(update: Update, context: CallbackContext) -> int:
    context.user_data['dinero'] = update.message.text
    keyboard = [["⏳ Menos de 1h al día"], ["⏳ 1-3h al día"], ["⏳ Más de 3h al día"]]
    await update.message.reply_text("¿Cuánto tiempo podrías dedicarle a un negocio digital?", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return TIEMPO

async def tiempo(update: Update, context: CallbackContext) -> int:
    context.user_data['tiempo'] = update.message.text
    keyboard = [["🏆 Sí, me encanta vender y persuadir"], ["🤔 Lo he hecho algunas veces, pero me gustaría mejorar"], ["❌ No me gusta vender, prefiero otra forma de ganar dinero"]]
    await update.message.reply_text("¿Te sientes cómoda vendiendo o recomendando cosas?", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return VENTAS

async def ventas(update: Update, context: CallbackContext) -> int:
    context.user_data['ventas'] = update.message.text
    keyboard = [["🎤 Me encanta hablar en público o en cámara"], ["📩 Prefiero comunicarme por mensajes o escribir"], ["🎭 Me gusta expresarme, pero no sé si en video o con fotos"], ["😶 Prefiero no exponerme demasiado"]]
    await update.message.reply_text("¿Cómo te sientes comunicando con otras personas?", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return COMUNICACION

async def comunicacion(update: Update, context: CallbackContext) -> int:
    context.user_data['comunicacion'] = update.message.text
    keyboard = [["🎨 Sí, siempre tengo ideas y me encanta crear"], ["🔄 A veces, pero necesito inspiración"], ["📊 No, prefiero seguir estrategias ya probadas"]]
    await update.message.reply_text("¿Te consideras una persona creativa?", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return CREATIVIDAD

async def creatividad(update: Update, context: CallbackContext) -> int:
    context.user_data['creatividad'] = update.message.text
    keyboard = [["📸 Me considero fotogénica y me gusta la idea"], ["👀 No sé si soy fotogénica, pero me interesa intentarlo"], ["❌ No me siento cómoda exponiéndome"]]
    await update.message.reply_text("¿Cómo te sientes con la idea de aparecer en fotos o videos?", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return APARICION

async def aparicion(update: Update, context: CallbackContext) -> int:
    context.user_data['aparicion'] = update.message.text
    await update.message.reply_text("Por último, ¿cuál es tu correo electrónico?")
    return EMAIL

async def email(update: Update, context: CallbackContext) -> int:
    email = update.message.text
    if "@" not in email or "." not in email:
        await update.message.reply_text("Por favor, ingresa un email válido.")
        return EMAIL

    context.user_data['email'] = email
    await update.message.reply_text("✅ Registro completado. ¡Gracias!")
    return FINAL

# 🔹 Configuración del bot
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
application = Application.builder().token(TELEGRAM_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, nombre)],
        EDAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, edad)],
        CIUDAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, ciudad)],
        REDES: [MessageHandler(filters.TEXT & ~filters.COMMAND, redes)],
        # ... (Se incluyen todos los estados en orden)
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)]
    },
    fallbacks=[]
)

application.add_handler(conv_handler)
application.run_polling()

