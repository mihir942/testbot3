import os
import logging
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR
)

logger = logging.getLogger(__name__)

# Default values for the webhook server.
DEFAULT_WEBHOOK_ADDR = "0.0.0.0"
DEFAULT_WEBHOOK_PORT = 8080

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f"Hello {update.effective_user.first_name}, you are amazing!")

def main():

    load_dotenv()
    TOKEN = os.environ.get("TOKEN")

    env = os.environ.get("ENV", "development").lower()

    # We retrieve the webhook server settings from the environment.
    webhook_addr = os.environ.get("WEBHOOK_ADDR", DEFAULT_WEBHOOK_ADDR)
    webhook_port = os.environ.get("WEBHOOK_PORT", DEFAULT_WEBHOOK_PORT)
    webhook_url = os.environ.get("WEBHOOK_URL")

    # We create an Updater instance with our Telegram token.
    updater = Updater(TOKEN, use_context=True)

    # We register our command handlers.
    updater.dispatcher.add_handler(CommandHandler("start", start))

    # We are going to use webhooks on production server
    # but long polling for development on local machine.
    if env == "production":
        # Start a small HTTP server to listen for updates via webhook.
        updater.start_webhook(
            listen=webhook_addr,
            port=webhook_port,
            url_path=TOKEN,
            webhook_url=f"{webhook_url}/{TOKEN}",
        )
        logger.info(f"Start webhook HTTP server - {webhook_addr}:{webhook_port}")
    else:
        # Start polling updates from Telegram.
        updater.start_polling()
        logger.info(f"Start polling updates")

    # Run the bot until you press Ctrl-C.
    # Or until the process receives SIGINT, SIGTERM or SIGABRT.
    updater.idle()


if __name__ == "__main__":
    main()
