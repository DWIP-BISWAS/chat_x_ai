import os
import re
from urllib.parse import urlparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# List of words to ignore in queries
IGNORE_WORDS = {"what", "is", "how", "to", "explain", "does", "the", "are", "why", "where", "who", "was", "can"}

# List of file extensions to remove from search queries (not URLs)
EXTENSIONS = (".html", ".php", ".txt", ".json", ".xml", ".css", ".js")

# Function to clean user input
def clean_query(query):
    words = re.split(r'\W+', query.lower())  # Split by non-alphanumeric characters
    filtered_words = [word for word in words if word not in IGNORE_WORDS]  # Remove ignored words
    return " ".join(filtered_words).strip()

# Function to clean URLs for searching (removes file extensions)
def clean_url_text(url):
    url_text = url.lower()
    for ext in EXTENSIONS:
        url_text = url_text.replace(ext, "")  # Remove extensions
    return url_text

# Function to find the relevant text file in the root directory
def get_category_file(query_keywords):
    for filename in os.listdir():  # Search in the root folder
        if filename.endswith(".txt"):  # Check for text files
            file_keywords = set(filename.replace(".txt", "").split(","))  # Extract keywords from filename
            if query_keywords & file_keywords:  # Check if any keyword matches
                return filename  # Return the matching file
    return None

# Function to read URLs from the correct category file
def read_urls(category_file):
    with open(category_file, "r", encoding="utf-8") as file:
        return file.read().splitlines()

# Function to search for relevant URLs in the category file
def search_urls(query):
    query_keywords = set(clean_query(query).split())  # Convert input to keyword set
    category_file = get_category_file(query_keywords)  # Find correct category file
    
    if category_file:
        urls = read_urls(category_file)  # Read URLs from the matched file
        return [(urlparse(url).netloc.replace("www.", "").split(".")[0].capitalize(), url) for url in urls]
    
    return []

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
    results = search_urls(user_input)

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
