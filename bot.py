import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from duckduckgo_search import DDGS  # DuckDuckGo Search

# Function to read URLs from the text file
def read_urls():
    with open("urls.txt", "r") as file:
        return file.read().splitlines()

# Function to scrape website content
def scrape_website(url):
    try:
        if not url.startswith("http"):
            url = f"https://{url}"

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return f"Error: Unable to access {url} (Status Code: {response.status_code})"

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)

        return text[:3000]  # Limit to 3000 characters to avoid spam
    except Exception as e:
        return f"Error scraping {url}: {e}"

# Function to search DuckDuckGo
def search_duckduckgo(query):
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=1))
        if results:
            return results[0]["href"], results[0]["body"]
        return None, None

# Command handler for /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! I'm your bot. Ask me about anything, and I'll fetch the info for you.")

# Message handler for user queries
async def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text.lower()
    urls = read_urls()

    # First, check URLs list
    for url in urls:
        content = scrape_website(url)
        if user_input in url or user_input.lower() in content.lower():
            await update.message.reply_text(f"Found this on {url}:\n{content[:1000]}...\n\nRead more: {url}")
            return

    # If not found, search DuckDuckGo
    search_url, search_summary = search_duckduckgo(user_input)
    if search_url:
        await update.message.reply_text(f"Couldn't find in URLs. Searched DuckDuckGo:\n\n{search_summary}\n\nMore: {search_url}")
    else:
        await update.message.reply_text(f"Sorry, no relevant info found on '{user_input}'.")

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
