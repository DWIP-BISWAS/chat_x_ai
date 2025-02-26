import os
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from bs4 import BeautifulSoup
import requests

# Function to read URLs from the text file
def read_urls():
    with open("urls.txt", "r") as file:
        urls = file.read().splitlines()
    return urls

# Function to clean user input by removing common question words
def clean_query(query):
    ignore_words = ["how to", "what is", "who is", "where is", "how are", "explain", "define", "meaning of"]
    for word in ignore_words:
        query = query.replace(word, "").strip()
    return query

# Function to scrape website content
def scrape_website(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            content = soup.get_text(separator="\n", strip=True)
            return content[:1500]  # Limit text to 1500 characters
        else:
            return f"Could not fetch data from {url}"
    except Exception as e:
        return f"Error scraping {url}: {e}"

# Contact information message
contact_message = (
    "💡 *Want to contribute or add missing topics?*\n"
    "📩 Message the developer:\n"
    "📞 **WhatsApp:** [Click Here](https://wa.me/918629986990)\n"
    "💬 **Telegram:** @+918629986990"
)

# Command handler for /start
async def start(update: Update, context: CallbackContext):
    start_message = (
        "👋 **Welcome to X.AI!**\n\n"
        "I'm X.AI, your assistant for finding answers to most of your questions. 🚀\n"
        "I'm currently under development, and you can help make me better! 🛠️\n\n"
        + contact_message
    )
    
    await update.message.reply_text(start_message, parse_mode="Markdown", disable_web_page_preview=True)

# Message handler for user queries
async def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text.lower()
    user_input = clean_query(user_input)  # Clean input query

    urls = read_urls()
    found = False

    for url in urls:
        content = scrape_website(url)
        if user_input in url or user_input in content.lower():
            await update.message.reply_text(
                f"**Here's what I found about {user_input}:**\n\n{content}...\n\n🔗 [Read more]({url})",
                parse_mode="Markdown",
                disable_web_page_preview=True  # Avoid large link previews
            )
            found = True
            break

    if not found:
        await update.message.reply_text(
            f"❌ No results found for '{user_input}'.\n\n"
            "💡 *Ask the developer to add this topic!*\n\n" + contact_message,
            parse_mode="Markdown",
            disable_web_page_preview=True
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
