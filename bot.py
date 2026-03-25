import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction="You are a helpful, friendly, and knowledgeable AI assistant. Answer questions clearly and concisely. Be conversational and engaging."
)

# Store chat sessions per user
chat_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_sessions[user_id] = model.start_chat(history=[])
    await update.message.reply_text(
        "👋 I'm Qual The Elder Sage Of Corruption.\n\n"
        "Human you could ask me anything and Use /clear to Zoltraak our conversation."
    )

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_sessions[user_id] = model.start_chat(history=[])
    await update.message.reply_text("🧹 Conversation cleared! Let's start fresh.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    # Create new session if user is new
    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[])

    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    try:
        response = chat_sessions[user_id].send_message(user_message)
        await update.message.reply_text(response.text)

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text(
            "⚠️ Sorry, something went wrong. Please try again."
        )

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
