import os
import time
import logging
import requests
from flask import Flask, jsonify
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = "7871708884:AAGIJqpeyL1K7Gj0vlGXivINqzUFGuCK_rQ"  # Replace with your bot token
ADMIN_CHAT_ID = "7660271363"  # Replace with your Telegram ID

# Bot statistics
message_count = 0
last_active_time = 0
error_log_file = "bot_errors.log"

# Flask API for monitoring
app = Flask(__name__)

# Set up logging
logging.basicConfig(filename=error_log_file, level=logging.ERROR)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Bot is online!')

def count_messages(update: Update, context: CallbackContext) -> None:
    global message_count, last_active_time
    message_count += 1
    last_active_time = time.time()

def get_status(update: Update, context: CallbackContext) -> None:
    now = time.time()
    active_status = "ðŸ’¬ Chatting now" if (now - last_active_time) < 10 else "ðŸ›‘ Inactive"

    update.message.reply_text(f"ðŸ“Š Bot Status:
- Messages Received: {message_count}
- Status: {active_status}")

def error_callback(update, context):
    logging.error(f"Error: {context.error}")
    
    # Send an alert to admin via Telegram
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": ADMIN_CHAT_ID, "text": f"âš ï¸ Bot Error: {context.error}"}
    requests.post(url, json=payload)

# Telegram bot setup
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("status", get_status))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, count_messages))
dp.add_error_handler(error_callback)

# Flask API Endpoints
@app.route('/status', methods=['GET'])
def api_status():
    now = time.time()
    active_status = "ðŸ’¬ Chatting now" if (now - last_active_time) < 10 else "ðŸ›‘ Inactive"
    return jsonify({"messages_received": message_count, "status": active_status})

@app.route('/errors', methods=['GET'])
def api_errors():
    if os.path.exists(error_log_file):
        with open(error_log_file, "r") as file:
            errors = file.readlines()
        return jsonify({"errors": errors[-5:]})  # Return last 5 errors
    return jsonify({"errors": []})

if __name__ == '__main__':
    updater.start_polling()  # Start the bot
    app.run(host="0.0.0.0", port=5000)  # Start the Flask API
