import os
import logging
from groq import Groq
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

groq_client = Groq(api_key=os.environ.get("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"))
TELEGRAM_TOKEN = os.environ.get("8779917489:AAFpkZXrD1PFpLmCOU7qMxm_DMAGEEMIiHo")

# Store conversation history per user
conversation_histories = {}

SYSTEM_PROMPT = """You are a helpful, friendly, and knowledgeable AI assistant. 
Answer questions clearly and concisely. Be conversational and engaging."""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversation_histories[user_id] = []
    await update.message.reply_text(
        "👋 I'm Qual The Elder Sage Of Corruption.\n\n"
        "Human you could ask me anything and Use /clear to Zoltraak our conversation."
    )

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversation_histories[user_id] = []
    await update.message.reply_text("🧹 Conversation cleared! Let's start fresh.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    # Initialize history if new user
    if user_id not in conversation_histories:
        conversation_histories[user_id] = []

    # Add user message to history
    conversation_histories[user_id].append({
        "role": "user",
        "content": user_message
    })

    # Keep last 20 messages to avoid token limits
    if len(conversation_histories[user_id]) > 20:
        conversation_histories[user_id] = conversation_histories[user_id][-20:]

    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *conversation_histories[user_id]
            ],
            max_tokens=1024,
            temperature=0.7
        )

        assistant_message = response.choices[0].message.content

        # Add assistant response to history
        conversation_histories[user_id].append({
            "role": "assistant",
            "content": assistant_message
        })

        await update.message.reply_text(assistant_message)

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


