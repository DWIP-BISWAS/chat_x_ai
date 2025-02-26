import os
import re
import string
from urllib.parse import urlparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# List of words to ignore in queries
IGNORE_WORDS = {"what", "is", "how", "to", "explain", "does", "the", "are", "why", "where", "who", "was", "can"}

# List of file extensions to remove from search queries (not URLs)
EXTENSIONS = (".html", ".php", ".txt", ".json", ".xml", ".css", ".js")

# Function to clean user input (removes punctuation and stopwords)
def clean_query(query):
    query = query.lower()  # Convert to lowercase
    query = query.translate(str.maketrans("", "", string.punctuation))  # Remove punctuation
    words = query.split()  # Split into words
    filtered_words = [word for word in words if word not in IGNORE_WORDS]  # Remove ignored words
    return filtered_words  # Return list of cleaned keywords

# Function to clean URLs for searching (removes file extensions)
def clean_url_text(url):
    url_text = url.lower()
    for ext in EXTENSIONS:
        url_text = url_text.replace(ext, "")  # Remove extensions
    return url_text

# Function to find files that match at least one keyword
def find_matching_files(keywords):
    matching_files = []
    for filename in os.listdir():  # Search in root directory
        if filename.endswith(".txt"):  # Check only text files
            file_keywords = filename.replace(".txt", "").lower().split("_")  # Split filename into words
            if any(keyword in file_keywords for keyword in keywords):  # If any keyword matches
                matching_files.append(filename)
    return matching_files

# Function to search for relevant URLs inside files
def search_urls_in_files(query_keywords):
    matching_files = find_matching_files(query_keywords)  # Find relevant files
    results = []

    for filename in matching_files:
        with open(filename, "r") as file:
            urls = file.read().splitlines()  # Read URLs from file

            for url in urls:
                lower_url = clean_url_text(url)  # Clean URL text before searching
                if all(keyword in lower_url for keyword in query_keywords):  # Must contain all keywords
                    # Extract site name for button text
                    parsed_url = urlparse(url)
                    site_name = parsed_url.path.split("/")[-1]  # Get last part of the path
                    if not site_name:
                        site_name = parsed_url.netloc.replace("www.", "").split(".")[0].capitalize()
                    results.append((site_name, url))

    return results

# Command handler for /start
async def start(update: Update, context: CallbackContext):
    welcome_message = (
        "**Welcome to X.AI!** 🤖\n"
        "I'm a coding and tutorial bot that helps find answers to most questions!\n"
        "I'm under development, and you can help make me better!\n\n"
        "📩 **Contact Developer:**"
    )
    
    keyboard = [
        [InlineKeyboardButton("WhatsApp", url="https://wa.me/918629986990")],
        [InlineKeyboardButton("Telegram", url="https://t.me/dwip_thedev")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_message, parse_mode="Markdown", reply_markup=reply_markup)

# Message handler for user queries
async def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text.lower()
    query_keywords = clean_query(user_input)  # Clean the query

    if not query_keywords:
        await update.message.reply_text("⚠️ *Please enter a valid search query!*", parse_mode="Markdown")
        return

    results = search_urls_in_files(query_keywords)

    if results:
        message = "**Here's what I found:**\n\n"
        keyboard = [[InlineKeyboardButton(f"Click here {i+1}", url=url)] for i, (_, url) in enumerate(results)]
    else:
        message = (
            f"⚠️ *I couldn't find an answer for '{user_input}'!*\n\n"
            "Please message the developer to add this topic! 📩"
        )
        keyboard = [
            [InlineKeyboardButton("WhatsApp", url="https://wa.me/918629986990")],
            [InlineKeyboardButton("Telegram", url="https://t.me/dwip_thedev")]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, parse_mode="Markdown", reply_markup=reply_markup)

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
