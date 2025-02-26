import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from duckduckgo_search import DDGS  # DuckDuckGo Search (no API needed)

# Function to read URLs from a text file
def read_urls():
    try:
        with open("urls.txt", "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to scrape website content using requests + BeautifulSoup
def scrape_website(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        content = soup.get_text(separator="\n", strip=True)
        
        return content[:1500]  # Limit to 1500 characters
    except Exception as e:
        return f"Error scraping {url}: {e}"

# Function to search using DuckDuckGo
def search_duckduckgo(query):
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=1))
    
    if results:
        return results[0]["title"], results[0]["href"], results[0]["body"][:500]
    return None

# Command handler for /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! I'm your bot. Ask me anything, and I'll fetch relevant info.")

# Message handler for user queries
async def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text.lower()
    urls = read_urls()

    # Check URLs first
    for url in urls:
        if user_input in url or user_input in scrape_website(url).lower():
            await update.message.reply_text(f"Here's what I found about {user_input}:\n{url}\n\n{scrape_website(url)}")
            return

    # If not found, search online
    result = search_duckduckgo(user_input)
    if result:
        title, link, snippet = result
        await update.message.reply_text(f"Here's what I found about {user_input}:\n{title}\n{link}\n\n{snippet}")
    else:
        await update.message.reply_text(f"Sorry, no relevant info found on '{user_input}'.")

# Main function to run the bot
def main():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")  # Get bot token from environment variable
    application = Application.builder().token(bot_token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
