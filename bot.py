import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from playwright.sync_api import sync_playwright

# Function to read URLs from the text file
def read_urls():
    with open("urls.txt", "r") as file:
        urls = file.read().splitlines()
    return urls

# Function to scrape website content
def scrape_website(url):
    try:
        if not url.startswith("http"):
            url = f"https://{url}"
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url)
            content = page.inner_text("body")  # Scrape all text in the body
            browser.close()
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

    found = False
    for url in urls:
        content = scrape_website(url)
        if user_input in url or user_input in content.lower():
            await update.message.reply_text(f"Here's what I found about {user_input}:\n\n{content[:1000]}...")
            found = True
            break

    if not found:
        available_topics = ", ".join([url.split(".")[1] for url in urls])  # Extract domain names
        await update.message.reply_text(
            f"Sorry, I couldn't find any information about {user_input}.\n\n"
            f"Available topics: {available_topics}"
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
