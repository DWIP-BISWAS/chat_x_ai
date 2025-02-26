import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# List of common words to ignore
IGNORE_WORDS = {"what", "is", "how", "to", "explain", "does", "the", "are", "why", "where", "who", "was", "can"}

# Folder where category files are stored
CATEGORY_FOLDER = "categories"

# Function to clean and extract keywords from query
def clean_query(query):
    words = re.split(r'\W+', query.lower())  # Split by non-alphanumeric characters
    return [word for word in words if word and word not in IGNORE_WORDS]

# Function to find the best category file based on query
def get_category_file(query_keywords):
    for filename in os.listdir(CATEGORY_FOLDER):
        file_keywords = set(filename.replace(".txt", "").split(","))  # Extract keywords from filename
        if query_keywords & file_keywords:  # If at least one keyword matches
            return os.path.join(CATEGORY_FOLDER, filename)
    return None  # No matching file found

# Function to search links inside the selected file
def search_in_file(category_file, query_keywords):
    if not category_file or not os.path.exists(category_file):
        return []

    results = []
    with open(category_file, "r") as file:
        for line in file:
            if any(keyword in line.lower() for keyword in query_keywords):  # Match against keywords
                results.append(line.strip())

    return results[:10]  # Return max 10 results

# Function to handle user queries
def search_urls(query):
    query_keywords = set(clean_query(query))
    category_file = get_category_file(query_keywords)  # Find correct category file
    
    if not category_file:
        return []  # No matching category file found
    
    return search_in_file(category_file, query_keywords)

# Command handler for /start
async def start(update: Update, context: CallbackContext):
    welcome_message = "**Welcome to X.AI!** 🤖\nI help you with coding tutorials!\n"
    keyboard = [[InlineKeyboardButton("Contact Developer", url="https://t.me/dwip_thedev")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_message, parse_mode="Markdown", reply_markup=reply_markup)

# Message handler for user queries
async def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text.lower()
    cleaned_query = clean_query(user_input)  # Extract keywords from query
    results = search_urls(user_input)

    if results:
        message = "**Here are some helpful links:**\n"
        keyboard = [[InlineKeyboardButton(f"Link {i+1}", url=url)] for i, url in enumerate(results)]
    else:
        message = f"⚠️ *No results for '{user_input}'!*\nMessage the developer to add this topic!"
        keyboard = [[InlineKeyboardButton("Contact Developer", url="https://t.me/dwip_thedev")]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, parse_mode="Markdown", reply_markup=reply_markup)

# Main function
def main():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
