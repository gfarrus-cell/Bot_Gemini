import os
import re
from datetime import time
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

from gemini_client import ask_gemini

# ===== Config =====
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TZ = ZoneInfo("America/Argentina/Buenos_Aires")

# Memoria en RAM (no persistente).
USER_WEIGHTS = {}  # {user_id: {"last": float, "history": [(iso_date, kg), ...]}}

# ===== Helpers =====
def parse_weight_arg(text: str) -> float | None:
    m = re.search(r"(-?\d+(?:[.,]\d+)?)", text)
    if not m:
        return None
    return float(m.group(1).replace(",", "."))

def parse_time_and_text(args: list[str]) -> tuple[time | None, str]:
    """Espera: /recordatorios HH:MM Texto del recordatorio"""
    if not args:
        return None, ""
    hhmm = args[0]
    txt = " ".join(args[1:]).strip()
    m = re.match(r"^([01]?\d|2[0-3]):([0-5]\d)$", hhmm)
    if not m:
        return None, " ".join(args).strip()
    hh, mm = int(m.group(1)), int(m.group(2))
    return time(hour=hh, minute=mm, tzinfo=TZ), txt

# ===== Handlers =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "¡Hola! Soy tu bot Gemini 🤖\n\n"
        "Comandos disponibles:\n"
        "• /planalimentos – Plan de alimentación base\n"
        "• /planentrenamiento – Rutina semanal sugerida\n"
        "• /seguimientopeso 115.2 – Guarda tu peso y te muestra el cambio\n"
        "• /recordatorios HH:MM texto – Te recuerdo todos los días\n"
        "• Escribime cualquier cosa y te contesto con Gemini"
    )
    await update.message.reply_text(msg)

async def plan_alimentos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    plan = (
        "Plan de alimentación base (orientativo):\n"
        "• Desayuno: huevos + tostadas integrales + café/té\n"
        "• Almuerzo: proteína magra (pollo/pescado) + verduras cocidas + quinoa/arroz integral\n"
        "• Merienda: yogur natural o queso magro + frutos secos (pequeña porción)\n"
        "• Cena: carne magra o legumbres + puré de calabaza/batata + verduras cocidas\n"
        "• Agua: 2–2.5L/día • Evitar ultraprocesados • 80–100g proteína/día aprox.\n"
        "Si querés, después lo personalizamos con tus restricciones."
    )
    await update.message.reply_text(plan)

async def plan_entrenamiento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    plan = (
        "Plan de entrenamiento (base, 5 días):\n"
        "• Lunes: Fuerza cuerpo completo (40–60’)\n"
        "• Martes: Cardio suave 30–45’ (caminar/bici) + movilidad 10’\n"
        "• Miércoles: Fuerza (énfasis tren superior) 40–60’\n"
        "• Jueves: HIIT liviano 20’ + core 10’ + movilidad 10’\n"
        "• Viernes: Fuerza (énfasis tren inferior) 40–60’\n"
        "• Sábado/Domingo: actividad recreativa + estiramientos 15’\n"
        "Progresá +5–10% volumen/2–3 semanas. Si querés, lo ajusto a tu equipo/tiempos."
    )
    await update.message.reply_text(plan)

async def seguimiento_peso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    kg = parse_weight_arg(update.message.text or "")
    if kg is None:
        await update.message.reply_text("Usá: /seguimientopeso 115.2")
        return

    hist = USER_WEIGHTS.setdefault(user_id, {"last": None, "history": []})
    prev = hist["last"]
    hist["last"] = kg
    from datetime import datetime
    hist["history"].append((datetime.now(TZ).date().isoformat(), kg))
    hist["history"] = hist["history"][-30:]

    if prev is None:
        await update.message.reply_text(f"Anotado ✅ Tu peso actual: {kg:.1f} kg.")
    else:
        diff = kg - prev
        flecha = "⬇️" if diff < 0 else ("⬆️" if diff > 0 else "➡️")
        await update.message.reply_text(
            f"Anotado ✅ {flecha} Cambio vs anterior: {diff:+.1f} kg (actual {kg:.1f} kg)."
        )

async def reminder_callback(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(chat_id=job.chat_id, text=f"⏰ Recordatorio: {job.data}")

async def recordatorios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    when, text = parse_time_and_text(context.args)
    if when is None:
        await update.message.reply_text("Usá: /recordatorios HH:MM tu recordatorio (ej: /recordatorios 09:00 tomar agua)")
        return
    if not text:
        await update.message.reply_text("Decime qué querés que te recuerde 😉")
        return

    context.job_queue.run_daily(
        reminder_callback,
        time=when,
        chat_id=update.effective_chat.id,
        name=f"reminder_{update.effective_chat.id}_{when.hour:02d}{when.minute:02d}_{abs(hash(text))%10000}",
        data=text,
        timezone=TZ,
    )
    await update.message.reply_text(f"Listo. Te lo recuerdo todos los días a las {when.strftime('%H:%M')}.")

async def gemini_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        return
    try:
        reply = await ask_gemini(text)
        await update.message.reply_text(reply[:4000])
    except Exception as e:
        await update.message.reply_text("Ups, falló la consulta a Gemini. Probá de nuevo en un rato.")
        print(f"[Gemini error] {e}")

def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("Falta TELEGRAM_TOKEN en variables de entorno")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("planalimentos", plan_alimentos))
    app.add_handler(CommandHandler("planentrenamiento", plan_entrenamiento))
    app.add_handler(CommandHandler("seguimientopeso", seguimiento_peso))
    app.add_handler(CommandHandler("recordatorios", recordatorios))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gemini_chat))

    print("Bot iniciado… 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()
