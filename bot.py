import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from ddg_search import ddg  # DuckDuckGo search (No API needed)

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
        content = soup.get_text().strip()
        
        # Limit text to 1000 chars but show "Read more" link
        if len(content) > 1000:
            return f"{content[:1000]}...\n\n[Read more]({url})"
        return f"{content}\n\n[Source]({url})"
    
    except Exception as e:
        return f"Error scraping {url}: {e}"

# Function to search DuckDuckGo (No API needed)
def duckduckgo_search(query):
    results = ddg(query, max_results=3)
    if results:
        return [f"[{r['title']}]({r['href']})" for r in results]
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
            await update.message.reply_text(f"Here's what I found about **{user_input}**:\n\n{content}", parse_mode="Markdown")
            return

    # If no info is found, search DuckDuckGo
    await update.message.reply_text(f"Searching DuckDuckGo for '**{user_input}**'...", parse_mode="Markdown")
    search_results = duckduckgo_search(user_input)

    if search_results:
        results_message = "\n".join(search_results)
        await update.message.reply_text(f"🔍 **Search results:**\n\n{results_message}", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"Sorry, no relevant info found on '**{user_input}**'.", parse_mode="Markdown")

# Main function to run the bot
def main():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")  # Use env variable for security
    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
