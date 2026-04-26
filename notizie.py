import asyncio
import feedparser
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURAZIONE ---
TOKEN = '8372751202:AAEbNHkmTZlXyCXnbK8ekm5uI9owwThK1kg'
MIO_CHAT_ID = 6310024951
FILE_MEMORIA = "notizie_inviate.txt"

# Lista dei giornali (Italiani e Internazionali)
FONTI = {
    "BBC News (Mondo)": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "New York Times": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "ANSA": "https://www.ansa.it/sito/ansait_rss.xml",
    "Corriere": "https://xml2.corriereobjects.it/rss/homepage.xml",
    "Repubblica": "https://www.repubblica.it/rss/homepage/rss2.0.xml",
}

def carica_cronologia():
    """Legge il file per vedere quali notizie abbiamo già inviato"""
    if not os.path.exists(FILE_MEMORIA):
        return set()
    with open(FILE_MEMORIA, "r") as f:
        return set(f.read().splitlines())

def salva_in_cronologia(link):
    """Aggiunge il link della notizia appena inviata al file"""
    with open(FILE_MEMORIA, "a") as f:
        f.write(link + "\n")

async def rispondi_con_notizie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Questa funzione scatta quando tu scrivi al bot"""
    
    # Controllo di sicurezza: se ti scrive qualcun altro, il bot lo ignora!
    if update.effective_chat.id != MIO_CHAT_ID:
        return

    # Avvisa che sta lavorando
    await update.message.reply_text("🌍 Cerco le ultime notizie in Italia e nel mondo... Attendi!")
    
    cronologia = carica_cronologia()
    nuove_notizie = []

    for nome, url in FONTI.items():
        feed = feedparser.parse(url)
        # Prende le ultime 3 notizie (meglio 3 per non inondare la chat vista l'aggiunta di fonti)
        for entry in feed.entries[:3]:
            if entry.link not in cronologia:
                testo = f"🗞 *{nome}*\n[{entry.title}]({entry.link})"
                nuove_notizie.append((testo, entry.link))

    if nuove_notizie:
        for msg, link in nuove_notizie:
            await context.bot.send_message(chat_id=MIO_CHAT_ID, text=msg, parse_mode='Markdown')
            salva_in_cronologia(link)
            # Una piccola pausa per evitare che Telegram ci blocchi per "spam"
            await asyncio.sleep(1)
        await update.message.reply_text("✅ Ricerca completata!")
    else:
        await update.message.reply_text("Nessuna nuova notizia trovata dall'ultima volta.")

if __name__ == "__main__":
    print("Avvio del bot... Ora il programma rimarrà in ascolto.")
    print("Vai su Telegram e scrivi /notizie al tuo bot!")
    
    # Costruiamo l'applicazione che "ascolta" Telegram
    app = Application.builder().token(TOKEN).build()
    
    # Diciamo al bot di eseguire la funzione quando riceve il comando /notizie
    app.add_handler(CommandHandler("notizie", rispondi_con_notizie))
    
    # (Opzionale) Reagisce anche se scrivi semplicemente la parola "notizie"
    app.add_handler(MessageHandler(filters.Text("notizie") | filters.Text("Notizie"), rispondi_con_notizie))
    
    # Questo comando blocca il programma tenendolo acceso e in ascolto perenne
    app.run_polling()