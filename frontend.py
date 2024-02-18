from gettext import dpgettext
from typing import Final
import configparser
import typing
from telegram import InlineKeyboardMarkup, InputFile, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, MessageHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackQueryHandler
import datetime
import requests
from io import BytesIO


from backend import insert_meal, get_meal_logs, create_database, reset_logs

# Initialize the database
create_database()

TOKEN: Final = '6666000684:AAG8VteJNEBthN266225DWEr9Hj6uM4Xo3Y'
BOT_USERNAME: Final = '@BitesByBytes_Bot'


# Frotnend Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello, Welcome to BitesByBytes! Simply just add this telebot to a group chat with your loved ones for your logging to start')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Simply just press /log and select your meals to start with the logging!\n\nDo contact me at @glennquahh if you need any help!')

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

async def breakfast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()  # acknowledge button press

    user_id = query.from_user.id
    user_states[user_id] = {'step': 'photo'}

    await query.message.edit_text('You have selected Breakfast! Please send me a photo of your meal!')

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

# ... (other code)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User({update.message.chat.id}) in {message_type} : "{text}"')

    user_id = update.message.from_user.id
    username = update.message.from_user.username

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
        if user_id in user_states and user_states[user_id]['step'] == 'description':
            description: str = text
            photo_file_id: str = user_states[user_id]['photo']
            meal_type: str = user_states[user_id]['meal_type']

            # Insert the meal information into the database
            insert_meal(user_id, username, meal_type, photo_file_id, description)

            # Reset user's state
            del user_states[user_id]
            
            await update.message.reply_text("Thank you for logging your meal!")
            return

        response: str = handle_response(text)
        if response is not None:
            print('Bot:', response)
            await update.message.reply_text(response)

async def print_logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    meal_logs = get_meal_logs()

    if meal_logs:
        for log in meal_logs:
            user_id, username, meal_type, meal_description, meal_photo = log
            message_text = f"User {username} - {meal_type}: {meal_description}"
            await update.message.reply_text(message_text)
            
            if meal_photo:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=meal_photo)
    else:
        await update.message.reply_text("No meal logs found.")


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

            # Insert the meal information into the database
            insert_meal(user_id, username, meal_type, photo_file_id, description)

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
    app.add_handler(CommandHandler('resetlogs', reset_logs_command))

    # Messages
    app.add_handler(MessageHandler(filters.ATTACHMENT, handle_photo))
    app.add_handler(MessageHandler(filters.ALL, handle_message))


    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)


