import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Function to read URLs from the text file
def read_urls():
    try:
        with open("urls.txt", "r") as file:
            return file.read().splitlines()
    except Exception as e:
        logger.error(f"Error reading URLs: {e}")
        return []

# Async function to scrape website content
async def scrape_website(url):
    try:
        if not url.startswith("http"):
            url = f"https://{url}"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            logger.info(f"Scraping: {url}")
            await page.goto(url, timeout=15000)
            
            # Wait for content to load
            await page.wait_for_load_state("networkidle")
            
            # Get page content
            content = await page.content()
            soup = BeautifulSoup(content, "html.parser")
            
            # Close browser
            await browser.close()

            # Extract text from paragraphs
            paragraphs = soup.find_all("p")
            clean_content = " ".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            return clean_content[:1500]  # Limit response length
            
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        return None

# Command handler for /start
async def start(update: Update, context: CallbackContext):
    try:
        await update.message.reply_text(
            "🌟 Hello! I'm your Smart URL Bot. Just ask me about any topic, "
            "and I'll find relevant information from my database!"
        )
        logger.info(f"Start command from user: {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Start command error: {e}")

# Message handler for user queries
async def handle_message(update: Update, context: CallbackContext):
    try:
        user_input = update.message.text.lower().strip()
        logger.info(f"Received query: {user_input}")

        urls = read_urls()
        if not urls:
            await update.message.reply_text("⚠️ My database is currently empty. Please add URLs to urls.txt.")
            return

        # Search for matching URLs
        matched_urls = [url for url in urls if user_input in url.lower()]

        # If no URL matches, search content
        if not matched_urls:
            for url in urls:
                content = await scrape_website(url)
                if content and user_input in content.lower():
                    matched_urls = [url]
                    break

        if matched_urls:
            content = await scrape_website(matched_urls[0])
            if content:
                await update.message.reply_text(
                    f"🔍 Here's what I found about '{user_input}':\n\n"
                    f"{content}\n\n"
                    f"Source: {matched_urls[0]}"
                )
                return

        # Fallback response
        available_topics = "\n".join([f"- {url.split('//')[-1].split('/')[0]}" for url in urls])
        await update.message.reply_text(
            f"❌ I couldn't find information about '{user_input}'.\n\n"
            "Available topics:\n"
            f"{available_topics}"
        )

    except Exception as e:
        logger.error(f"Message handler error: {e}")
        await update.message.reply_text("⚠️ An error occurred. Please try again later.")

def main():
    try:
        # Get bot token from environment
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

        # Create application
        application = Application.builder().token(bot_token).build()

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # Start polling
        logger.info("Bot is starting...")
        application.run_polling()

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        if 'application' in locals():
            application.stop()

if __name__ == "__main__":
    main()
