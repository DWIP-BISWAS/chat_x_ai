import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from playwright.async_api import async_playwright

# Function to read URLs from file
def read_urls():
    with open("urls.txt", "r") as file:
        urls = file.read().splitlines()
    return urls

# Function to scrape website data
async def scrape_website(url):
    try:
        if not url.startswith("http"):
            url = f"https://{url}"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )

            page = await context.new_page()
            await page.goto(url, timeout=90000, wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle", timeout=60000)

            raw_text = await page.inner_text("body")

            await browser.close()

            processed_text = "\n".join([line.strip() for line in raw_text.splitlines() if line.strip()])
            
            return processed_text[:1000]  # Limit output to avoid Telegram spam

    except Exception as e:
        return f"Error scraping {url}: {e}"

# Function to search Google and get the first result
async def google_search(query):
    try:
        google_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )

            page = await context.new_page()
            await page.goto(google_url, timeout=90000, wait_until="domcontentloaded")

            # Extract the first search result link
            search_results = await page.locator("h3").all()
            if not search_results:
                await browser.close()
                return None

            first_result = await search_results[0].evaluate("node => node.parentElement.href")
            await browser.close()
            return first_result

    except Exception as e:
        return None

# Command handler for /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! Send me a topic, and I'll fetch relevant info!")

# Message handler for user queries
async def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text.lower()
    urls = read_urls()

    found = False
    for url in urls:
        content = await scrape_website(url)  # Await async function
        if user_input in url or user_input in content.lower():
            await update.message.reply_text(f"Here's what I found about '{user_input}':\n\n{content}...")
            found = True
            break

    if not found:
        # Try Google Search
        await update.message.reply_text(f"Searching Google for '{user_input}'...")
        google_url = await google_search(user_input)

        if google_url:
            content = await scrape_website(google_url)
            if "Error scraping" not in content:
                await update.message.reply_text(f"Here's what I found from Google:\n\n{content}...\n\n(Source: {google_url})")
            else:
                await update.message.reply_text(f"Google found this link, but I couldn't fetch the content:\n{google_url}")
        else:
            await update.message.reply_text(f"Sorry, no relevant info found on '{user_input}'.")

# Main function to run bot
def main():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
