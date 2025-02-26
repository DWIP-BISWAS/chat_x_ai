import os
import time
import logging
import requests
from flask import Flask, jsonify
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Get bot token and admin ID from environment variables
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# Bot statistics
message_count = 0
last_active_time = 0
error_log_file = "bot_errors.log"

# Flask API for monitoring
app = Flask(__name__)

# Set up logging
logging.basicConfig(filename=error_log_file, level=logging.ERROR)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Bot is online.')

def count_messages(update: Update, context: CallbackContext) -> None:
    global message_count, last_active_time
    message_count += 1
    last_active_time = time.time()

def get_status(update: Update, context: CallbackContext) -> None:
    now = time.time()
    active_status = "Chatting now" if (now - last_active_time) < 10 else "Inactive"

    update.message.reply_text(f"Bot Status:\n- Messages Received: {message_count}\n- Status: {active_status}")

def error_callback(update, context):
    logging.error(f"Error: {context.error}")
    
    # Send an alert to admin via Telegram
    if TOKEN and ADMIN_CHAT_ID:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": ADMIN_CHAT_ID, "text": f"Bot Error: {context.error}"}
        requests.post(url, json=payload)

# Telegram bot setup
if TOKEN:
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
    active_status = "Chatting now" if (now - last_active_time) < 10 else "Inactive"
    return jsonify({"messages_received": message_count, "status": active_status})

@app.route('/errors', methods=['GET'])
def api_errors():
    if os.path.exists(error_log_file):
        with open(error_log_file, "r") as file:
            errors = file.readlines()
        return jsonify({"errors": errors[-5:]})  # Return last 5 errors
    return jsonify({"errors": []})

if __name__ == '__main__':
    if TOKEN:
        updater.start_polling()  # Start the bot
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))  # Start the Flask API with Railway's assigned port
