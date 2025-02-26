import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import asyncio

# Function to read URLs from the text file
def read_urls():
    with open("urls.txt", "r") as file:
        urls = file.read().splitlines()
    return urls

# Function to search for relevant URLs based on keywords
def search_urls(query, urls):
    keywords = query.lower().split()  # Break user input into words
    results = []

    for url in urls:
        lower_url = url.lower()
        if any(keyword in lower_url for keyword in keywords):  # Match any keyword
            results.append(url)

    return results

# Command handler for /start
async def start(update: Update, context: CallbackContext):
    welcome_message = (
        "**Welcome to X.AI!** 🤖\n"
        "I'm a coding and tutorial bot that helps find answers to most questions!\n"
        "I'm under development, and you can help make me better!\n\n"
        "📩 **Contact Developer:**\n"
        "👉 **WhatsApp:** [wa.me/918629986990](https://wa.me/918629986990)\n"
        "👉 **Telegram:** @YourUsername"
    )
    await update.message.reply_text(welcome_message, parse_mode="Markdown")

# Message handler for user queries
async def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text.lower()
    urls = read_urls()

    results = search_urls(user_input, urls)

    if results:
        response = "**Here's what I found:**\n\n" + "\n".join([f"🔗 {url}" for url in results])
    else:
        response = (
            f"⚠️ *I couldn't find an answer for '{user_input}'!*\n\n"
            "Please message the developer to add this topic! 📩\n"
            "👉 **WhatsApp:** [wa.me/918629986990](https://wa.me/918629986990)\n"
            "👉 **Telegram:** @dwip_the_dev"
        )

    await update.message.reply_text(response, parse_mode="Markdown")

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
