from gettext import dpgettext
from typing import Final
from tables import Filters
from telegram import InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, MessageHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackQueryHandler


TOKEN: Final = '6666000684:AAG8VteJNEBthN266225DWEr9Hj6uM4Xo3Y'
BOT_USERNAME: Final = '@BitesByBytes_Bot'


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello, Welcome to BitesByBytes! Simply just add this telebot to a group chat with your loved ones for your logging to start')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Simply just press /log and select your meals to start with the logging!\n\nDo contact me at @glennquahh if you need any help!')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Contact me at @glennquahh for any help!')

async def log_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    options = [
        [{'text': 'Log Breakfast', 'callback_data': 'log_breakfast'}, 
         {'text': 'Log Lunch', 'callback_data': 'log_lunch'}],
        [{'text': 'Log Dinner', 'callback_data': 'log_dinner'}, 
         {'text': 'Log Snack', 'callback_data': 'log_snack'}]
    ]
    
    reply_markup = InlineKeyboardMarkup(options)
    await update.message.reply_text('Choose an option to log:', reply_markup=reply_markup)


async def handle_keyboard_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    selected_option = query.data
    
    if selected_option == 'log_breakfast':
        await breakfast_command(update, context)  # Call the function with parentheses
    elif selected_option == 'log_lunch':
        await lunch_command(update, context)  # Call the function with parentheses
    elif selected_option == 'log_dinner':
        await dinner_command(update, context)  # Call the function with parentheses
    elif selected_option == 'log_snack':
        await snack_command(update, context)  # Call the function with parentheses
    else:
        if query is not None:
            await query.answer('Invalid selection.')


async def breakfast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Insert Breakfast description and picture')
    # You can add additional steps here, such as waiting for the description and picture
    # and then processing them accordingly.

    # For example, you can send a message asking for description:
    await update.message.reply_text('Please enter a description for your breakfast:')

    # You can then handle user input using a callback or by checking the next message received.
    # Once you receive the description, you can ask for the picture.

    # Similarly, ask for the picture:
    await update.message.reply_text('Now, please send a picture of your breakfast:')
    
    # You can then handle the picture and description accordingly in the following messages.


async def lunch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('You have selected Lunch!')

async def dinner_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Contact me at @glennquahh for any help!')

async def snack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Contact me at @glennquahh for any help!')

# Responses

def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'hello' in processed:
        return 'Hello there!'
    
    if 'bye' in processed:
        return 'Goodbye!'
    
    return 'I do not understand you!'

# Handlers

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User({update.message.chat.id}) in {message_type} : "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print('Bot:', response)
    await update.message.reply_text(response)

# logging errors

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('log', log_command))
    app.add_handler(CommandHandler('breakfast', breakfast_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(CallbackQueryHandler(handle_keyboard_selection))


    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)