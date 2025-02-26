import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

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
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! I'm your bot. Ask me about anything, and I'll fetch the relevant info for you.")

# Message handler for user queries
async def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text.lower()
    urls = read_urls()

    # Check if any URL matches the user's query
    found = False
    for url in urls:
        if user_input in url:  # Check if the query is part of the URL
            content = scrape_website(url)
            if content:
                await update.message.reply_text(f"Here's what I found about {user_input}:\n\n{content[:1000]}...")  # Limit response length
                found = True
                break

    if not found:
        await update.message.reply_text(f"Sorry, I couldn't find any information about {user_input}.")

# Main function to run the bot
def main():
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")  # Use environment variable for security
    application = Application.builder().token(bot_token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
