import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from playwright.async_api import async_playwright  # Use Async API

# Function to read URLs from the text file
def read_urls():
    with open("urls.txt", "r") as file:
        urls = file.read().splitlines()
    return urls

# Function to scrape website content
async def scrape_website(url):
    try:
        if not url.startswith("http"):
            url = f"https://{url}"

        async with async_playwright() as p:
            # Launch browser with stealth settings
            browser = await p.chromium.launch(headless=True, timeout=60000)  # Increase timeout
            context = await browser.new_context()

            # Block unnecessary resources (e.g., images, stylesheets) to speed up loading
            await context.route("**/*", lambda route: route.abort() 
                if route.request.resource_type in {"image", "stylesheet", "font", "script"} 
                else route.continue_()
            )

            page = await context.new_page()

            # Navigate to the URL with a longer timeout
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")  # Wait for DOM content to load

            # Wait for the page to fully load
            await page.wait_for_load_state("networkidle")  # Wait for network activity to stop

            # Scrape the body text
            content = await page.inner_text("body")
            await browser.close()
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
        content = await scrape_website(url)  # Await the async function
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
