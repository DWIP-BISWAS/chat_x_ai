import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Function to clean query (removes common words like "what is", "how to", etc.)
def clean_query(query):
    stop_words = {"what", "is", "how", "to", "are", "do", "does", "the", "a", "an", "why", "where", "who", "which"}
    words = query.lower().split()
    filtered_words = [word for word in words if word not in stop_words]
    return " ".join(filtered_words)

# Function to read URLs from the text file
def read_urls():
    try:
        with open("urls.txt", "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to search for relevant URLs based on keywords
def search_urls(query, urls):
    keywords = clean_query(query).split()  # Clean query before searching
    results = []

    for url in urls:
        lower_url = url.lower()
        if all(keyword in lower_url for keyword in keywords):  
            # ✅ Remove file extensions from display text (but keep actual URL)
            display_text = re.sub(r'\.(html|php|txt|json|xml|css|js)$', '', url, flags=re.IGNORECASE)
            results.append((display_text, url))  # Store as (text, actual URL)

    return results

# Command handler for /start
async def start(update: Update, context: CallbackContext):
    message = (
        "**Welcome to X.ai!** 🤖\n\n"
        "I'm a **coding and tutorial bot** that helps answer your questions. "
        "I'm still under development, and if you're interested, you can participate to help make me better!\n\n"
        "**Just message my developer:**\n"
        "📩 WhatsApp: +918629986990\n"
        "📩 Telegram: @dwip_thedev"
    )
    await update.message.reply_text(message, parse_mode="Markdown")

# Message handler for user queries
async def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text.lower()
    urls = read_urls()

    results = search_urls(user_input, urls)

    if results:
        message = "**Here's what I found:**\n\n"
        keyboard = [[InlineKeyboardButton(f"Click here {i+1}: {text}", url=url)] for i, (text, url) in enumerate(results)]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(
            "❌ I couldn't find anything for your query.\n\n"
            "📢 **Ask the developer to add this topic!**\n"
            "📩 WhatsApp: +918629986990\n"
            "📩 Telegram: @dwip_thedev",
            parse_mode="Markdown"
        )

# Main function to run the bot
def main():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")  # Use environment variable for security
    application = Application.builder().token(bot_token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
