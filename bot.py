import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Function to read URLs from a text file
def read_urls():
    with open("urls.txt", "r") as file:
        return file.read().splitlines()

# Function to scrape website content
def scrape_website(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return f"Error {response.status_code}: Unable to access {url}"
        
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()[:1000]  # Limit to 1000 characters
    except Exception as e:
        return f"Error scraping {url}: {e}"

# Function to search Google when no info is found
def google_search(query):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.select("a[href^='http']")

        links = [link["href"] for link in results if "google" not in link["href"]]
        return links[:3]  # Return top 3 results
    except Exception as e:
        return None

# Command handler for /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! I'm your bot. Ask me about anything, and I'll fetch the relevant info for you.")

# Message handler for user queries
async def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text.lower()
    urls = read_urls()

    # Check if the query matches any saved URLs
    for url in urls:
        content = scrape_website(url)
        if user_input in url or user_input in content.lower():
            await update.message.reply_text(f"Here's what I found about {user_input}:\n\n{content}...")
            return

    # If no info is found, search Google
    await update.message.reply_text(f"Searching Google for '{user_input}'...")
    google_results = google_search(user_input)

    if google_results:
        results_message = "\n".join(google_results)
        await update.message.reply_text(f"Here are some links:\n{results_message}")
    else:
        await update.message.reply_text(f"Sorry, no relevant info found on '{user_input}'.")

# Main function to run the bot
def main():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")  # Use env variable for security
    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
