import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Function to read URLs from the text file
def read_urls():
    with open("urls.txt", "r") as file:
        urls = file.read().splitlines()
    return urls

# Function to scrape website content
def scrape_website(url):
    try:
        response = requests.get(f"https://{url}")
        soup = BeautifulSoup(response.text, "html.parser")
        # Extract relevant content (e.g., paragraphs)
        paragraphs = soup.find_all("p")
        content = " ".join([p.get_text() for p in paragraphs])
        return content
    except Exception as e:
        return f"Error scraping {url}: {e}"

# Command handler for /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! I'm your bot. Ask me about anything, and I'll fetch the relevant info for you.")

# Message handler for user queries
def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text.lower()
    urls = read_urls()

    # Check if the user is asking about HTML
    if "html" in user_input:
        url = next((u for u in urls if "w3schools.com/html" in u), None)
        if url:
            content = scrape_website(url)
            update.message.reply_text(f"Here's what I found about HTML:\n\n{content[:1000]}...")  # Limit response length
        else:
            update.message.reply_text("Sorry, I couldn't find any HTML tutorial links.")
    else:
        update.message.reply_text("I'm not sure what you're asking. Try asking about HTML!")

# Main function to run the bot
def main():
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")  # Use environment variable for security
    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher

    # Add handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
