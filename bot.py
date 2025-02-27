import os
import re
from urllib.parse import urlparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# List of words to ignore in queries
IGNORE_WORDS = {"what", ".", "!", ";", "`", "~", "@", "is", "how", "to", "#", "$", "%", "^", "&", "*", "(", ")", "-","_", "=", "+", "|", "]", "[", "{", "}", ":", "?", "explain",",", "does", "the", "are", "why", "where", "who", "was", "can"}

# List of file extensions to remove from search queries
EXTENSIONS = (".html", ".php", ".txt", ".json", ".xml", ".css", ".js")

# List of compulsory files to always check
COMPULSORY_FILES = ["urls.txt", "wiki1.txt"]

# Function to clean user input
def clean_query(query):
    words = re.split(r'\W+', query.lower())
    filtered_words = [word for word in words if word not in IGNORE_WORDS]
    return " ".join(filtered_words).strip()

# Function to clean URLs
def clean_url_text(url):
    url_text = url.lower()
    for ext in EXTENSIONS:
        url_text = url_text.replace(ext, "")
    return url_text

# Function to find matching files
def get_matching_files(query_keywords):
    matching_files = []
    for filename in os.listdir():
        if filename.endswith(".txt") and any(keyword in filename.lower() for keyword in query_keywords):
            matching_files.append(filename)
    
    # Add compulsory files only if they are not already in the matching_files list
    for comp_file in COMPULSORY_FILES:
        if comp_file not in matching_files:
            matching_files.append(comp_file)
    
    return matching_files

# Function to search URLs inside files
def search_urls(query):
    query_keywords = clean_query(query).split()
    matching_files = get_matching_files(query_keywords)
    results = set()  # Use a set to store unique URLs

    for file in matching_files:
        with open(file, "r") as f:
            urls = f.read().splitlines()
            for url in urls:
                if all(keyword in clean_url_text(url) for keyword in query_keywords):
                    parsed_url = urlparse(url)
                    site_name = parsed_url.path.split("/")[-1] or parsed_url.netloc.split(".")[0].capitalize()
                    results.add((site_name, url))  # Add to set to ensure uniqueness

    return list(results)  # Convert set back to list before returning

# /start command
async def start(update: Update, context: CallbackContext):
    welcome_message = """
**Welcome to X.AI!** 🤖
I'm a wiki bot that helps you find answers to most questions!
I'm still under development, and you can help make me better by contributing to this project! Use /contribute to learn more.

Quick Tips: Use "_" or "-" instead of " " (space). It helps me understand your query better.
Use /help to see available commands!

📩 **Contact Developer:**
"""
    
    keyboard = [
        [InlineKeyboardButton("WhatsApp", url="https://wa.me/918629986990")],
        [InlineKeyboardButton("Telegram", url="https://t.me/dwip_thedev")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_message, parse_mode="Markdown", reply_markup=reply_markup)

# /help command
async def help_command(update: Update, context: CallbackContext):
    help_text = """
**Available Commands:**
/start - Start the bot
/help - Show this help message
/info - Get bot info
/contribute - Contribute to X.AI
/contact - Contact the developer

Just type a question, and I'll try to find an answer for you! 😊
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

# /info command
async def info_command(update: Update, context: CallbackContext):
    info_text = """
**X.AI Bot Info:**
🤖 **Version:** 1.0
📌 **Purpose:** Coding and tutorial assistant
💡 **Status:** Under development
🛠 **Developer:** [Dwip](https://t.me/dwip_thedev)

Want to contribute? Use /contribute!
"""
    await update.message.reply_text(info_text, parse_mode="Markdown")

# /contribute command
async def contribute_command(update: Update, context: CallbackContext):
    contribute_text = """
**Contribute to X.AI!** 🚀
Want to help improve this bot? You can contribute by:
- Suggesting new features
- Providing coding resources
- Reporting bugs

📩 Contact the developer to contribute!
"""
    keyboard = [
        [InlineKeyboardButton("Contact Dev", url="https://t.me/dwip_thedev")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(contribute_text, parse_mode="Markdown", reply_markup=reply_markup)

# /contact command
async def contact_command(update: Update, context: CallbackContext):
    contact_text = "**Need help? Contact the developer!** 📩"
    keyboard = [
        [InlineKeyboardButton("WhatsApp", url="https://wa.me/918629986990")],
        [InlineKeyboardButton("Telegram", url="https://t.me/dwip_thedev")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(contact_text, parse_mode="Markdown", reply_markup=reply_markup)

# Handle user queries
async def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text.lower()
    cleaned_query = clean_query(user_input)

    results = search_urls(cleaned_query)

    if results:
        message = "**Here's what I found:**\n\n"
        keyboard = [[InlineKeyboardButton(f"Click here {i+1}", url=url)] for i, (_, url) in enumerate(results)]
    else:
        message = f"⚠️ *I couldn't find an answer for '{user_input}'!*\n\nPlease message the developer to add this topic! 📩"
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

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("contribute", contribute_command))
    application.add_handler(CommandHandler("contact", contact_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
