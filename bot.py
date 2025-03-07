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

# 📝 Nombre de la hoja de cálculo
SHEET_NAME = "14-MFH08mqKa0cTJLVIHtd724FasnnOORN7R14WPwS_s"
sheet = client.open_by_key(SHEET_NAME).sheet1

# 🔹 Estados del flujo de conversación
(
    INICIO, NOMBRE, EDAD, CIUDAD, REDES, RED_PRINCIPAL, USUARIO, SEGUIDORES, 
    DINERO, TIEMPO, VENTAS, COMUNICACION, CREATIVIDAD, APARICION, CONTENIDO, EMAIL
) = range(16)

async def start(update: Update, context: CallbackContext) -> int:
    keyboard = [["🟢 Empezar"]]
    await update.message.reply_text(
        "¡Hola! Te haré algunas preguntas para encontrar la mejor oportunidad para ti. Pulsa el botón para comenzar.",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return INICIO  # Ahora sí está incluido en `states={}`

async def iniciar_preguntas(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("¡Genial! Comencemos. ¿Cuál es tu nombre o apodo?")
    return NOMBRE

async def nombre(update: Update, context: CallbackContext) -> int:
    context.user_data['nombre'] = update.message.text
    await update.message.reply_text("¿Cuántos años tienes?")
    return EDAD

async def edad(update: Update, context: CallbackContext) -> int:
    try:
        edad = int(update.message.text)
        if edad < 18:
            await update.message.reply_text("Debes ser mayor de 18 años para continuar. ¡Gracias!")
            return ConversationHandler.END
        context.user_data['edad'] = edad
        await update.message.reply_text("¿En qué ciudad y país vives?")
        return CIUDAD
    except ValueError:
        await update.message.reply_text("Por favor, ingresa una edad válida en números.")
        return EDAD

async def ciudad(update: Update, context: CallbackContext) -> int:
    context.user_data['ciudad'] = update.message.text
    keyboard = [
        ["📸 Instagram", "🎥 TikTok", "🐦 Twitter"],
        ["📢 Telegram", "🔗 Facebook", "💬 Reddit"],
        ["✅ Listo"]
    ]
    await update.message.reply_text(
        "¿Qué redes sociales usas o crees que podrían ser útiles para monetizar? (Puedes elegir varias y luego pulsa '✅ Listo')",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
    )
    return REDES

async def redes(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    if text == "✅ Listo":
        await update.message.reply_text("¿En qué red social te sientes más cómoda o eres más activa?")
        return RED_PRINCIPAL
    else:
        context.user_data.setdefault('redes', []).append(text)
        return REDES

async def red_principal(update: Update, context: CallbackContext) -> int:
    context.user_data['red_principal'] = update.message.text
    await update.message.reply_text("Ahora dime tu usuario en esa red social (@usuario).")
    return USUARIO

async def usuario(update: Update, context: CallbackContext) -> int:
    context.user_data['usuario'] = update.message.text
    keyboard = [["Menos de 1,000", "Entre 1,000 y 5,000"], ["Entre 5,000 y 10,000", "Más de 10,000"]]
    await update.message.reply_text("¿Cuántos seguidores tienes en la red social donde eres más activa?", 
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    return SEGUIDORES

async def dinero(update: Update, context: CallbackContext) -> int:
    context.user_data['seguidores'] = update.message.text
    keyboard = [["✅ Sí, ya tengo una fuente de ingresos"], ["⭕ No, pero me gustaría empezar"]]
    await update.message.reply_text("¿Actualmente ganas dinero online?", 
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return TIEMPO

async def tiempo(update: Update, context: CallbackContext) -> int:
    context.user_data['dinero'] = update.message.text
    keyboard = [["⏳ Menos de 1h al día"], ["⏳ 1-3h al día"], ["⏳ Más de 3h al día"]]
    await update.message.reply_text("¿Cuánto tiempo podrías dedicarle a un negocio digital?", 
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return VENTAS

async def ventas(update: Update, context: CallbackContext) -> int:
    context.user_data['tiempo'] = update.message.text
    keyboard = [["🏆 Sí, me encanta vender y persuadir"], ["🤔 Lo he hecho algunas veces, pero me gustaría mejorar"], ["❌ No me gusta vender"]]
    await update.message.reply_text("¿Te sientes cómoda vendiendo o recomendando cosas a otras personas?", 
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return COMUNICACION

async def comunicacion(update: Update, context: CallbackContext) -> int:
    context.user_data['ventas'] = update.message.text
    keyboard = [["🎤 Me encanta hablar en público o en cámara"], ["📩 Prefiero comunicarme por mensajes"], ["🎭 Me gusta expresarme, pero no sé cómo"], ["😶 Prefiero no exponerme demasiado"]]
    await update.message.reply_text("¿Cómo te sientes comunicando con otras personas?", 
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return CREATIVIDAD

async def creatividad(update: Update, context: CallbackContext) -> int:
    context.user_data['comunicacion'] = update.message.text
    keyboard = [["🎨 Sí, siempre tengo ideas y me encanta crear"], ["🔄 A veces, pero necesito inspiración"], ["📊 No, prefiero seguir estrategias ya probadas"]]
    await update.message.reply_text("¿Te consideras una persona creativa para generar ideas de contenido o estrategias?", 
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return EMAIL

async def email(update: Update, context: CallbackContext) -> int:
    email = update.message.text
    if "@" not in email or "." not in email:
        await update.message.reply_text("Por favor, ingresa un email válido.")
        return EMAIL
    context.user_data['email'] = email
    await guardar_en_sheets(update, context)
    await update.message.reply_text("✅ Registro completado. ¡Gracias!")
    return ConversationHandler.END

async def guardar_en_sheets(update: Update, context: CallbackContext):
    datos = [context.user_data.get(key, '') for key in ['nombre', 'edad', 'ciudad', 'redes', 'red_principal', 'usuario', 'seguidores', 'dinero', 'tiempo', 'ventas', 'comunicacion', 'creatividad', 'email']]
    sheet.append_row(datos)

application = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        INICIO: [MessageHandler(filters.TEXT, iniciar_preguntas)],
        NOMBRE: [MessageHandler(filters.TEXT, nombre)],
        EDAD: [MessageHandler(filters.TEXT, edad)],
        CIUDAD: [MessageHandler(filters.TEXT, ciudad)],
        REDES: [MessageHandler(filters.TEXT, redes)],
    },
    fallbacks=[]
)

application.add_handler(conv_handler)
application.run_polling()











