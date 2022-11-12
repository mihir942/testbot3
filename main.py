import os
import logging
import datetime
import gspread
import math

from dotenv import load_dotenv
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
header_row = mysheet.row_values(1)

SECTION, NAME = range(2)
YOURSELF, STARTDATETIME, ENDDATETIME, CONFIRM, PERSON = range(5)

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

    all_section_types = mysheet.col_values(5)[1:]
    all_section_types = list(set(all_section_types))
    all_section_types.sort()
    keyboard = [[InlineKeyboardButton(sect,callback_data=sect) for sect in all_section_types]]
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
def newoff_handler(update: Update, context: CallbackContext) -> int:

    keyboard = [[InlineKeyboardButton("Yes",callback_data="Yes"),InlineKeyboardButton("No",callback_data="No")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f"Are you applying for yourself?",reply_markup=reply_markup)

    return YOURSELF

# this is a CallbackQueryHandler
def yourself(update: Update, context: CallbackContext) -> int:
    # getting user reply
    query = update.callback_query
    query.answer()

    if query.data == "Yes":
        # select date
        numdays = 14
        base = datetime.datetime.today()
        update.callback_query.message.reply_text(f"Type in start date and time like this: 130522 1400")
        return STARTDATETIME

    elif query.data == "No":
        # select person applying on behalf of
        return PERSON

# this is a MessageHandler
def start_date_time(update: Update, context: CallbackContext) -> int:

    # getting user reply
    start_dt = update.message.text

    # checking if our user reply is valid, in (1) format, (2) date, (3) time.
    if is_valid_date_time(start_dt):
            # store user selected start date,time
            context.user_data['start_dt'] = start_dt
            # input end date, time
            context.bot.send_message(update.effective_user.id,f"Start: {start_dt}\nType in end date and time")
            return ENDDATETIME
    else:
        context.bot.send_message(update.effective_user.id,"Invalid date/time.")
        context.bot.send_message(update.effective_user.id,f"Type in start date and time like this: 130522 1400")
        return STARTDATETIME

# this is a MessageHandler
def end_date_time(update: Update, context: CallbackContext) -> int:

    # getting user reply
    end_dt = update.message.text
    start_dt = context.user_data['start_dt']

    if is_valid_date_time(end_dt) and difference_in_hours(start_dt=start_dt,end_dt=end_dt) % 12 == 0:
        # store user selected end date,time
        context.user_data['end_dt'] = end_dt

        off_duration = calculate_off_duration(start_dt=start_dt, end_dt=end_dt)
        context.user_data['off_duration'] = off_duration

        keyboard = [[InlineKeyboardButton("Yes",callback_data="Yes"),InlineKeyboardButton("No",callback_data="No")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(f"Is this correct?\n\nStart: {start_dt}\nEnd: {end_dt}\nOff Duration: {off_duration} OFF",reply_markup=reply_markup)

        return CONFIRM
    else:
        start_dt = context.user_data['start_dt']
        context.bot.send_message(update.effective_user.id,"Invalid date/time.")
        context.bot.send_message(update.effective_user.id,f"Start: {start_dt}\nType in end date and time")
        return ENDDATETIME

# this is a CallbackQueryHandler
def confirm(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    if query.data == "Yes":
        context.bot.send_message(update.effective_user.id,"Thanks.")
        # TODO: Update in spreadsheet
        start_dt = context.user_data['start_dt']
        end_dt = context.user_data['end_dt']
        off_duration = context.user_data['off_duration']

        new_apply = start_dt + "-" + end_dt + " (" + str(off_duration) + " OFF)"

        userid = update.effective_user.id
        cell = mysheet.find(str(userid))
        row_num = cell.row
        col_num = header_row.index('Absences') + 1

        # get current Absences
        cell_value = mysheet.cell(row_num,col_num).value

        if cell_value != None:
            # turn into list
            current_list = cell_value.split('\n')

            # append to list
            current_list.append(new_apply)

            # update cell with "\n".join(list)
            mysheet.update_cell(row_num,col_num,"\n".join(current_list))
        else:
            mysheet.update_cell(row_num,col_num,new_apply)

        # clear persistent data
        context.user_data.clear()
        return ConversationHandler.END
    else:
        context.bot.send_message(update.effective_user.id,"Let's restart.")
        context.bot.send_message(update.effective_user.id,f"Type in start date and time like this: 130522 1400")
        return STARTDATETIME

# this is a CallbackQueryHandler
def person(update: Update, context: CallbackContext) -> int:
    return ConversationHandler.END

# this is a CommandHandler
def cancel_handler(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Cancelled. Back to normal.")
    return ConversationHandler.END

# this is a CommandHandler
def getmyoffs_handler(update: Update, context: CallbackContext) -> None:
    userid = str(update.effective_user.id)
    cell = mysheet.find(userid)
    row = cell.row
    col = header_row.index('Absences') + 1

    cell_value = mysheet.cell(row,col).value
    update.message.reply_text(f"These are your current offs/leaves etc:\n\n{cell_value}")

# helper function
def fetch_all() -> list:
    return mysheet.get_all_values()

# helper function
def valid_times() -> list:
    times = list()
    for i in range(0,24):
        time = str(i) + '00'
        if i < 10: time = '0' + time
        times.append(time)
    return times

# helper function
def is_valid_date_time(dt: str) -> bool:

    items = [x for x in dt.strip().split(' ')]
    items = list(filter(None,items))

    # getting the valid dates
    base = datetime.datetime.today()
    valid_dates = [base + datetime.timedelta(days=x) for x in range(14)]
    valid_dates = [x.strftime('%d%m%y') for x in valid_dates]

    return (len(items) == 2) and (items[0] in valid_dates) and (items[1] in valid_times())

# helper function
def user_to_datetime(usertext: str):
    # user text in the form of 171122 1400
    return datetime.datetime.strptime(usertext,"%d%m%y %H%M")

# helper function
def difference_in_hours(start_dt: str, end_dt: str) -> int:
    start_dt = user_to_datetime(usertext=start_dt)
    end_dt = user_to_datetime(usertext=end_dt)

    delta = end_dt - start_dt
    diff_in_hours = int(delta.total_seconds() / 60 / 60)
    return diff_in_hours

# helper function
def calculate_off_duration(start_dt: str,end_dt: str) -> float:
    diff = difference_in_hours(start_dt=start_dt, end_dt=end_dt)
    offs = round(diff/24, 1)
    return offs

def main() -> None:

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

    newOffConvoHandler = ConversationHandler(
        entry_points=[CommandHandler('newoff',newoff_handler)],
        states = {
            YOURSELF: [CallbackQueryHandler(yourself)],
            STARTDATETIME: [MessageHandler(Filters.text & ~Filters.command,start_date_time)],
            ENDDATETIME: [MessageHandler(Filters.text & ~Filters.command, end_date_time)],
            CONFIRM: [CallbackQueryHandler(confirm)],
            PERSON: [CallbackQueryHandler(person)]
        },
        fallbacks=[CommandHandler('cancel',cancel_handler)]
    )

    updater.dispatcher.add_handler(registerConvoHandler)
    updater.dispatcher.add_handler(newOffConvoHandler)
    updater.dispatcher.add_handler(CommandHandler('getmyoffs',getmyoffs_handler))

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
