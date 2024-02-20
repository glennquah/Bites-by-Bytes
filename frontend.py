from gettext import dpgettext
from typing import Final
import typing
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputFile, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, MessageHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackQueryHandler
from datetime import datetime


from backend import insert_meal, get_meal_logs, create_database, reset_logs, delete_meal

# Initialize the database
create_database()

TOKEN: Final = '6666000684:AAG8VteJNEBthN266225DWEr9Hj6uM4Xo3Y'
BOT_USERNAME: Final = '@BitesByBytes_Bot'


# Frotnend Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello, Welcome to BitesByBytes! Simply just use this telebot with your loved ones for your logging to start! Use /help to see the available commands.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('''Available commands:
    - /start: Start the bot
    - /log: Log a new meal
    - /printlogs: View logged meals
    - /delete <id>: Delete a meal log by ID
    - /help: Show this message''')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Contact me at @glennquahh for any help!')

async def reset_logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reset_logs()
    await update.message.reply_text("Database has been reset.")

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

user_states = {}
log_details_callbacks = {}


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('Handling photo...')
    message = update.message
    user_id = message.from_user.id

    if user_id in user_states and user_states[user_id]['step'] == 'photo':
        user_states[user_id]['step'] = 'description'
        user_states[user_id]['photo'] = message.photo[-1].file_id  # Save the file_id of the last photo

        await message.reply_text('Great! Now send me a brief description of your meal!')
    else:
        await message.reply_text("Hello, make sure that this is a photo and not in a pdf / html format.")

async def breakfast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()  # acknowledge button press

    user_id = query.from_user.id
    user_states[user_id] = {'step': 'photo', 'meal_type': 'Breakfast'}

    await query.message.edit_text('You have selected Breakfast! Please send me a photo of your meal!')

async def lunch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()  # acknowledge button press

    user_id = query.from_user.id
    user_states[user_id] = {'step': 'photo', 'meal_type': 'Lunch'}

    await query.message.edit_text('You have selected Lunch! Please send me a photo of your meal!')

async def dinner_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()  # acknowledge button press

    user_id = query.from_user.id
    user_states[user_id] = {'step': 'photo', 'meal_type': 'Dinner'}

    await query.message.edit_text('You have selected Dinner! Please send me a photo of your meal!')

async def snack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()  # acknowledge button press

    user_id = query.from_user.id
    user_states[user_id] = {'step': 'photo', 'meal_type': 'Snack'}

    await query.message.edit_text('You have selected Snack! Please send me a photo of your meal!')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    bot_mentioned = BOT_USERNAME in text

    print(f'User({update.message.chat.id}) in {message_type} : "{text}"')

    user_id = update.message.from_user.id
    username = update.message.from_user.username

    if message_type == 'group' and not bot_mentioned:
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
            if response is not None:
                print('Bot:', response)
                await update.message.reply_text(response)
        else:
            return
    else:
        if user_id in user_states and user_states[user_id]['step'] == 'description':
            description: str = text
            photo_file_id: str = user_states[user_id]['photo']
            meal_type: str = user_states[user_id]['meal_type']
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Insert the meal information into the database
            insert_meal(user_id, username, meal_type, photo_file_id, description, date)

            # Reset user's state
            del user_states[user_id]
            
            await update.message.reply_text("Thank you for logging your meal!")
            return

        response: str = handle_response(text)
        if response is not None:
            print('Bot:', response)
            await update.message.reply_text(response)

async def print_logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    meal_logs = get_meal_logs()  # This function should fetch meal logs from your database
    global log_details_callbacks

    if meal_logs:
        message_text = "<b>Meal Logs:</b>\n"
        buttons = []
        for log in meal_logs:
            id, _, username, meal_type, _, _, date_str = log
            date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            formatted_date = date_obj.strftime("%m-%d")
            callback_data = f"detail_{id}"  # Use actual database ID for callback data
            log_details_callbacks[callback_data] = log
            buttons.append([InlineKeyboardButton(f"{formatted_date} : {meal_type} | {username}", callback_data=callback_data)])
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(message_text, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.message.reply_text("No meal logs found.")

async def handle_log_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    callback_data = query.data
    log = log_details_callbacks.get(callback_data)

    if log:
        id, user_id, username, meal_type, meal_description, meal_photo, date = log
        detail_message = f"<b>ID:</b> {id}\n<b>Date:</b> {date}\n<b>Username:</b> {username}\n<b>Meal Type:</b> {meal_type}\n<b>Description:</b> {meal_description}\n\nUse /delete {id} to remove this entry."
        await context.bot.send_message(chat_id=query.message.chat_id, text=detail_message, parse_mode='HTML')
        if meal_photo:
            await context.bot.send_photo(chat_id=query.message.chat_id, photo=meal_photo)
    else:
        await query.edit_message_text(text="Details not found.")
    await query.answer()

async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        log_id = context.args[0]
        # Assuming you have a function delete_meal(log_id) in your backend.py
        delete_meal(log_id)  # Implement this function in your backend
        await update.message.reply_text(f"Deleted entry with ID {log_id}.")
    else:
        await update.message.reply_text("Please specify the ID of the entry you want to delete. Use /delete <id>.")

# Responses

def handle_response(text: str) -> typing.Optional[str]:
    processed: str = text.lower()

    if 'hello' in processed:
        return 'Hello there!'
    
    if 'bye' in processed:
        return 'Goodbye!'
    
    return None  # Return None if the input is not recognized


# Handlers

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User({update.message.chat.id}) in {message_type} : "{text}"')

    user_id = update.message.from_user.id

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
            if response is not None:
                print('Bot:', response)
                await update.message.reply_text(response)
        else:
            return
    else:
        # Check if the user is in 'description' state
        if user_id in user_states and user_states[user_id]['step'] == 'description':
            description: str = text
            meal_type: str = user_states[user_id]['meal_type']
            photo_file_id: str = user_states[user_id]['photo']
            username = update.message.from_user.username
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Insert the meal information into the database
            insert_meal(user_id, username, meal_type, photo_file_id, description, date)

            # Reset user's state
            del user_states[user_id]
            
            await update.message.reply_text("Thank you for logging your meal!")
            return

        response: str = handle_response(text)
        if response is not None:
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
    app.add_handler(CallbackQueryHandler(handle_keyboard_selection, pattern='^log_.*'))
    app.add_handler(CommandHandler('printlogs', print_logs_command))
    app.add_handler(CallbackQueryHandler(handle_log_detail_callback, pattern='^detail_.*'))
    app.add_handler(CommandHandler('resetlogs', reset_logs_command))
    app.add_handler(CommandHandler('delete', delete_command))

    # Messages
    app.add_handler(MessageHandler(filters.ATTACHMENT, handle_photo))
    app.add_handler(MessageHandler(filters.ALL, handle_message))


    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)


