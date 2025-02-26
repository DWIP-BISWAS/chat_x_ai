import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# List of words to ignore in queries
IGNORE_WORDS = {"what", "is", "how", "to", "explain", "does", "the", "are", "why", "where", "who", "was", "can"}

# List of file extensions to remove
EXTENSIONS = {".html", ".php", ".txt", ".json", ".xml", ".css", ".js"}

# Folder where category files are stored
CATEGORY_FOLDER = "categories"

# Function to clean user input
def clean_query(query):
    words = re.split(r'\W+', query.lower())  # Split by non-alphanumeric characters
    filtered_words = [word for word in words if word not in IGNORE_WORDS]  # Remove common words
    cleaned_query = " ".join(filtered_words)

    # Remove file extensions
    for ext in EXTENSIONS:
        cleaned_query = cleaned_query.replace(ext, "")

    return cleaned_query.strip()

# Function to get category file based on query
def get_category_file(query):
    query_keywords = set(query.split())

    # Check which file contains at least one matching keyword
    for filename in os.listdir(CATEGORY_FOLDER):
        file_keywords = set(filename.replace(".txt", "").split(","))  # Extract keywords from filename
        if query_keywords & file_keywords:  # Check for intersection
            return os.path.join(CATEGORY_FOLDER, filename)
    
    return None  # If no category file matches

# Function to read URLs from the relevant category file
def read_urls(category_file):
    if category_file and os.path.exists(category_file):
        with open(category_file, "r") as file:
            urls = file.read().splitlines()
        return urls
    return []

# Function to search for relevant URLs in the correct category file
def search_urls(query):
    category_file = get_category_file(query)  # Find correct category file
    if not category_file:
        return []  # No matching category file

    urls = read_urls(category_file)
    results = []

    for url in urls:
        lower_url = url.lower()
        if any(keyword in lower_url for keyword in query.split()):  # Check if any keyword is present
            results.append(url)

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
    cleaned_query = clean_query(user_input)  # Clean the query
    results = search_urls(cleaned_query)

    if results:
        message = "**Here's what I found:**\n\n"
        keyboard = [[InlineKeyboardButton(f"Click here {i+1}", url=url)] for i, url in enumerate(results)]
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
