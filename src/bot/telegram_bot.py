import asyncio
import os

from telebot import types
from telebot.async_telebot import AsyncTeleBot

from src.parsing.parsing_data import strings_parsing, conv_parsing
from src.db.user_database_handler import UserDatabaseHandler
from src.util.image_processing import image_proc
from src.util.text_constants import *

flags = {'adding_pic': -1, 'changing_conv': -2, 'adding_strings': -3, 'asking_to_withdraw': -4, 'if_withdrawing': -5}

handler = UserDatabaseHandler("../db/user_colors.sql")
TOKEN = '7932733884:AAFsKDKeuFDvlbtue-jgf-bU2XKdMdzVgrM'

bot = AsyncTeleBot(TOKEN)

length = 100
width = 100


def update_user_flag(user_id, flag_name, state: bool) -> None:  # флаги для ввода ин-фы от юзера
    change_id = flags[flag_name]
    cur_st = bin(handler.get_user_settings(user_id))[2:]
    cur_st = list(cur_st.zfill(4))
    cur_st[change_id] = str(int(state))
    cur_st = ''.join(cur_st)
    handler.update_user_settings(user_id, int(cur_st, 2))


def check_user_flag(user_id, flag_name) -> int:
    settings = bin(handler.get_user_settings(user_id))[2:]
    settings = settings.zfill(4)
    return int(settings[flags[flag_name]], 2)


@bot.message_handler(commands=['start'])
async def help_handler(message):  # базовые кнопки
    user_id = message.from_user.id
    handler.insert_user(user_id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    help_button = types.KeyboardButton(HELP_BUTTON_TEXT)
    add_strings_button = types.KeyboardButton(ADD_STRINGS_BUTTON_TEXT)
    start_image_processing = types.KeyboardButton(PROCESS_BUTTON_TEXT)
    explain = types.KeyboardButton(EXPLAIN_BUTTON_TEXT)
    markup.add(start_image_processing, add_strings_button, help_button, explain)
    await bot.send_message(message.chat.id, text=WELCOME_MESSAGE.format(message.from_user), reply_markup=markup)


@bot.message_handler(content_types=['text'])
async def command_handler(message):
    user_id = message.chat.id

    if not any(check_user_flag(user_id, flag) for flag in
               ['adding_pic', 'changing_conv', 'adding_strings', 'asking_to_withdraw']):  # чек кнопок
        if message.text == HELP_BUTTON_TEXT or message.text == '/help':
            await bot.send_message(user_id, text=HELP_MESSAGE_TEXT, parse_mode='Markdown')

        elif message.text == ADD_STRINGS_BUTTON_TEXT or message.text == '/add':
            update_user_flag(user_id, "adding_strings", True)
            await bot.send_message(user_id, text=ADD_STRINGS_MESSAGE_TEXT)

        elif message.text == PROCESS_BUTTON_TEXT or message.text == '/process':
            update_user_flag(user_id, 'changing_conv', True)
            await bot.send_message(user_id, text=PROCESS_MESSAGE_TEXT)

        elif message.text == EXPLAIN_BUTTON_TEXT or message.text == '/explain':
            await bot.send_message(user_id, text=EXPLAIN_MESSAGE_TEXT)

        else:
            await bot.send_message(user_id, text=BAD_COMMAND_MESSAGE_TEXT)

    elif message.text == '/stop' and not check_user_flag(message.chat.id, "adding_strings"):
        update_user_flag(message.chat.id, "changing_conv", False)
        update_user_flag(message.chat.id, "asking_to_withdraw", False)
        update_user_flag(message.chat.id, "adding_strings", False)
        update_user_flag(message.chat.id, "adding_pic", False)
        await bot.send_message(user_id, text=PROCESSING_STOP_MESSAGE)

    elif check_user_flag(message.chat.id, "adding_strings"):
        if message.text == "/stop":
            await bot.send_message(message.chat.id, text=STOP_ADDING_MESSAGE)
            update_user_flag(message.chat.id, "adding_strings", False)
        else:
            text_data = strings_parsing(message.text)
            if text_data:
                for [i, j] in text_data:
                    handler.insert_available(message.chat.id, i, j)
                    continue
            else:
                await bot.send_message(message.chat.id, text=WRONG_FORMAT_MESSAGE)


    elif check_user_flag(user_id, 'changing_conv'):
        text_data = conv_parsing(message.text)
        if text_data:
            global length, width
            length, width = text_data
            await bot.send_message(user_id, text=USE_STRINGS_Q_MESSAGE)
            update_user_flag(user_id, 'changing_conv', False)
            update_user_flag(user_id, 'asking_to_withdraw', True)
        else:
            await bot.send_message(user_id, text=WRONG_DATA_MESSAGE)


    elif check_user_flag(user_id, 'asking_to_withdraw'):
        if message.text.lower() == "да":
            update_user_flag(user_id, 'if_withdraw', True)
            await bot.send_message(user_id, text=USE_STRINGS_MESSAGE)
            update_user_flag(user_id, 'asking_to_withdraw', False)
            update_user_flag(user_id, 'adding_pic', True)
        elif message.text.lower() == "нет":
            update_user_flag(user_id, 'if_withdraw', False)
            await bot.send_message(user_id, text=NO_USE_STRINGS_MESSAGE)
            update_user_flag(user_id, 'asking_to_withdraw', False)
            update_user_flag(user_id, 'adding_pic', True)
        else:
            await bot.send_message(user_id, text=WRONG_DATA_MESSAGE)
    else:
        await bot.send_message(user_id, text=BAD_COMMAND_MESSAGE_TEXT)


@bot.message_handler(content_types=['photo'])
async def handle_image(message):
    if check_user_flag(message.chat.id, 'adding_pic'):
        file_info = await bot.get_file(message.photo[-1].file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        image_path = f'received_image{message.chat.id}.jpg'
        pdf_path = f'output_image.pdf{message.chat.id}.pdf'
        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        image_proc(image_path, pdf_path, message.chat.id, None, (length, width), 1,
                   check_user_flag(message.chat.id, 'if_withdraw') * 100)
        with open(pdf_path, 'rb') as pdf_file:
            await bot.send_document(message.chat.id, pdf_file)
        os.remove(image_path)
        os.remove(pdf_path)
        update_user_flag(message.chat.id, 'adding_pic', False)
        await bot.send_message(message.chat.id, text=DONE_MESSAGE)
    else:
        await bot.send_message(message.chat.id, text=TOO_EARLY_MESSAGE)


@bot.message_handler(func=lambda message: True)
async def error_handler(message):
    await bot.send_message(message.chat.id, text=MEME_MESSAGE)


asyncio.run(bot.infinity_polling())
