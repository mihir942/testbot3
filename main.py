import os
import logging
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, ConversationHandler, Filters, CallbackQueryHandler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR
)

logger = logging.getLogger(__name__)

# Default values for the webhook server.
DEFAULT_WEBHOOK_ADDR = "0.0.0.0"
DEFAULT_WEBHOOK_PORT = 8080

googledict = {
  "type": "service_account",
  "project_id": "testbot3-367616",
  "private_key_id": "9a001aeddcc4ab5f96ad7aa1f3a77b9abaf7d3fd",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDUeR8oo8GIuZqu\nYW5qovZSwaWdAgzSteHmEtyR8/taAx7KiDhDwO8bDsfFDKGA9toLw15cmzudWuoQ\nFn2saQogD2jNeBG96mojzGZbDIDimvHSEs6R6vcrnBzasfKplbjotk4CLbJZlza2\ncm92OZPXbJVTCPR1/ss3pmtvABUjJUWAcgZiFd3ROGvq+65HjR7jWNhdWiPe7qeQ\n9DTPi9ckAGovumIXOqvNlzonJkacXa1muVqHi7PbiG7nnM/eSCND8EsEeld3IQYX\nqa83npEPuzuCfdE1G5f2UECz100sY7u/5YwhoA6RIIYeaBLxldn95fRi4yWqQQeg\n0fpVIUkxAgMBAAECggEAD7Tzf3jZk/6qh2UW+UWaQYRkto5h/cqpzC0NRrHbXSxZ\nYJ4A0MtosZ6eWHwGTWcSN+flqCFmnwuLPYy4FiB+ud+Bvxy27Qvw9DwGPglW1smf\nAklXIXTV+FCWVnlsp6o0jOl7K1CO/G4AAq1DfaEkg3qYsFZ7YeSnx7GjBAXkyh/y\n+vwKn9NNt/l4E66vbuT/NAQFBaFlv5TwNoyn6xaMnRjv/j3LQMdch1fNcYFzvyZ9\nv8JnsU6TrK422PzYFMaXJaR1JzTcVoJzpIgNiM2Jm8c+4E3v7ZaDumecyOV1CNqp\nKBIzFk7zexCbGEv9kT8wlXjp7u+ZrPoQC8DieKwdFQKBgQDw9/BvTC2QJczXtDOg\nD7dQj0MrQINENog1EGlK1zf9cVZtDiBD/otxZHKxtb0bdKN3vGhcKJEYBgIBryPU\n8UvCstJBso9j8QnjpLnAlPOc7kUZp3U/3JoYB4emo5FuL9INZrV0mnd0AgB4Bc73\ng/vbbnbAaUA2md7NCb/LZTDBTQKBgQDhuiK8QLm1coA5R8TkZ1e5DzVQBpxiqgql\nu1kZnpROLW/LDiQ3j9It487gU8XPuN5D+M2YNJzlj0d967l7WUYYFWKiatF3a8ls\nnJ5DbQs77K5poxXEAWNFeAGROboVqQfimHjig94EW8kwkQtAD4SunfB01PM0yIH8\nJGJKiyQ1dQKBgG3YaHcj38VNJfLSh5IYd/U2SWVHFE+dGDwwTf862qAi8UXnYZf9\nSi2Xn50Y/qqsYfQsI9qW94Ve/70qzIe+s01+3M/sCOeDMoHeTnrWq7LG/yLxrkY9\nVtVLYW/6MkprbDKFtoQAAiIU44fTBgTY2o+t7F5L3GTHgcQwBIlAiJglAoGBAM9X\nceaoMa2pEn0LHqGLB7o2bQsoN2gtt4AKukpdLu8sr16+i6f51N9QPUwzxyUKNCgN\nl5Ry55e557qT15mlJEylACgepG/ks22v43Qd6s7Nllv0cN7NQ4mhNRdYBkU1McgD\ntC6lYD9yrDiPUt0yI/ddnm1C2m+mqjeYmCzO6KCtAoGBAJjFUNLkCrt+rTILAv3m\nagy+z0ZTl8PcvAjT+rC/qs+rl/V6sgrg38XYRoeBqpStaD9eKYnz4vvk2NqAldIf\nzrs19n5FZEaqDBvnUFGVwwaLq9GY3EfyZkkdvPzpj/4t2ZC1FRb5gDGpH+6HiQI5\nWxBGWa5lPkX3I7AixWaFpZKA\n-----END PRIVATE KEY-----\n",
  "client_email": "testbot3@testbot3-367616.iam.gserviceaccount.com",
  "client_id": "105399838713012761357",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/testbot3%40testbot3-367616.iam.gserviceaccount.com"
}

# must include both fields of scope (feeds and auth/drive)
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(googledict, scope)
client = gspread.authorize(creds)
mysheet = client.open("RAW").worksheet("biodata")

SECTION, NAME = range(2)

# this is a CommandHandler
def start_handler(update: Update, context: CallbackContext):
    update.message.reply_text(f"Hi, {update.effective_user.first_name}!")

    userid = str(update.message.from_user.id)
    all_userid = mysheet.col_values(4)

    registered = userid in all_userid
    if not registered:
        context.bot.send_message(update.effective_user.id,f"Please type /register to register yourself")

# this is a CommandHandler
def register_handler(update: Update, context: CallbackContext) -> int:
    userid = str(update.message.from_user.id)
    all_userid = mysheet.col_values(4)

    keyboard = [[
        InlineKeyboardButton("1",callback_data="1"),
        InlineKeyboardButton("2",callback_data="2"),
        InlineKeyboardButton("3",callback_data="3"),
        InlineKeyboardButton("PO",callback_data="PO")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    registered = userid in all_userid
    if not registered:
        update.message.reply_text("Not registered. Key in your section number",reply_markup=reply_markup)
        return SECTION
    else:
        update.message.reply_text("Already registered.")
        return ConversationHandler.END

# this is a CallbackQueryHandler
def section(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    context.bot.send_message(update.effective_user.id,f"You've chosen section {query.data}...")

    all_values = fetch_all()
    all_names = [row[0] + " " + row[1] for row in all_values]
    keyboard = [[InlineKeyboardButton(all_names[i],callback_data=str(i))] for i in range(len(all_values)) if all_values[i][4] == query.data]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.reply_text("Choose who you are",reply_markup=reply_markup)

    return NAME

# this is a CallbackQueryHandler
def name(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    all_values = fetch_all()
    index = int(query.data)
    name = all_values[index][0] + " " + all_values[index][1]

    context.bot.send_message(update.effective_user.id,f"Hi, {name}.")
    userid = update.effective_user.id
    mysheet.update_cell(index+1,4,userid)
    context.bot.send_message(update.effective_user.id,f"You're now registered.")

    return ConversationHandler.END

# this is a CommandHandler
def cancel_handler(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Cancelled. Back to normal.")
    return ConversationHandler.END

# helper function
def fetch_all() -> list:
    return mysheet.get_all_values()

# helper function
def fetch_section_rows(section: str) -> list:
    all_values = fetch_all()
    section_rows = [row for row in all_values if str(row[4]) == str(section)]
    return section_rows

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

    registerConvoHandler = ConversationHandler(
        entry_points=[CommandHandler('start',start_handler),CommandHandler('register',register_handler)],
        states={
            SECTION: [CallbackQueryHandler(section)],
            NAME: [CallbackQueryHandler(name)]
        },
        fallbacks=[CommandHandler('cancel',cancel_handler)]
    )

    updater.dispatcher.add_handler(registerConvoHandler)

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

'''
Workflow:

/start (if registered, 'Hi!'. if not registered, then run /register command):
/register
- Ask for section.
- Depending on section number inputted, fetch and display list of names from section
- Ask for the number from the list
- Once number keyed in, register their telegram userid with the spreadsheet

/newoff
- q1: are you applying for yourself? (yes=continue wif q2. no=ask for section,name)
- q2: start date and time 021122 1400
- q3: end date and time 031122 1400

/newleave
- q1: are you applying for yourself?
- q2: start date and time 021122 1400
- q3: start date and time 031122 1400

/newmc
- q1: are you applying for yourself?
- q2: start date 021122
- q3: end date 021122

/newma
- q1: are you applying for yourself?
- q2: date and time 031122 1600

/edit
- q1: choose from list to edit
- q2: carry on with the relevant questions from above

/cancel, to cancel at anytime

'''
