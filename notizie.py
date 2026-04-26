import asyncio
import feedparser
import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURAZIONE ---
# Usiamo os.environ.get per prendere il TOKEN dalle impostazioni di Render (sicurezza!)
TOKEN = os.environ.get('TOKEN')
MIO_CHAT_ID = 6310024951
FILE_MEMORIA = "notizie_inviate.txt"

FONTI = {
    "BBC": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "NYT": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "ANSA": "https://www.ansa.it/sito/ansait_rss.xml",
    "Corriere": "https://xml2.corriereobjects.it/rss/homepage.xml",
    "Repubblica": "https://www.repubblica.it/rss/homepage/rss2.0.xml",
}

# --- PARTE FLASK (Per Render) ---
app_web = Flask(__name__)
@app_web.route('/')
def home():
    return "Il bot è attivo!"

def run_web():
    app_web.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

# --- FUNZIONI BOT ---
def carica_cronologia():
    if not os.path.exists(FILE_MEMORIA): return set()
    with open(FILE_MEMORIA, "r") as f: return set(f.read().splitlines())

def salva_in_cronologia(link):
    with open(FILE_MEMORIA, "a") as f: f.write(link + "\n")

async def rispondi_con_notizie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != MIO_CHAT_ID: return
    await update.message.reply_text("🌍 Cerco notizie...")
    cronologia = carica_cronologia()
    for nome, url in FONTI.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            if entry.link not in cronologia:
                await context.bot.send_message(chat_id=MIO_CHAT_ID, text=f"🗞 *{nome}*\n[{entry.title}]({entry.link})", parse_mode='Markdown')
                salva_in_cronologia(entry.link)
                await asyncio.sleep(1)
    await update.message.reply_text("✅ Fatto!")

if __name__ == "__main__":
    # Avvia Flask in un thread separato
    threading.Thread(target=run_web).start()
    
    # Avvia il bot
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("notizie", rispondi_con_notizie))
    app.run_polling()
