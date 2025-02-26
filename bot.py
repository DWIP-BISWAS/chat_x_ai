import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Function to read URLs from the text file
def read_urls():
    try:
        with open("urls.txt", "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to scrape website content
def scrape_website(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        content = soup.get_text(separator="\n", strip=True)[:2000]  # Limit to 2000 chars
        return f"🔗 {url}\n\n{content}..."
    except Exception as e:
        return f"Error fetching {url}: {e}"

# Command handler for /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! I'm X.ai, your personal bot.")

# Message handler for user queries
async def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text.lower()
    urls = read_urls()

    for url in urls:
        if user_input in url:
            content = scrape_website(url)
            await update.message.reply_text(content)
            return

    await update.message.reply_text(
        f"Sorry, I don't have information on '{user_input}' yet.\n\n"
        "Please contact the developer to add it to the database."
    )

# Main function to run the bot
def main():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
