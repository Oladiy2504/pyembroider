import asyncio
import concurrent.futures
import os

from telebot import types
from telebot.async_telebot import AsyncTeleBot

from src.db.user_database_handler import UserDatabaseHandler
from src.parsing.parsing_data import strings_parsing, two_numbers_parsing
from src.util.image_processing import image_proc
from src.util.text_constants import *

flags = {'adding_pic': -1, 'changing_canvas': -2, 'adding_strings': -3, 'asking_to_withdraw': -4}

handler = UserDatabaseHandler("../db/user_colors.sql")
TOKEN = '7932733884:AAFsKDKeuFDvlbtue-jgf-bU2XKdMdzVgrM'

bot = AsyncTeleBot(TOKEN)


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
    # Увеличиваем количество одновременно обрабатываемых потоков
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
    loop = asyncio.get_running_loop()
    loop.set_default_executor(executor)

    user_id = message.from_user.id
    handler.insert_user(user_id)

    update_user_flag(message.chat.id, "changing_canvas", False)
    update_user_flag(message.chat.id, "asking_to_withdraw", False)
    update_user_flag(message.chat.id, "adding_strings", False)
    update_user_flag(message.chat.id, "adding_pic", False)

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
               ['adding_pic', 'changing_canvas', 'adding_strings', 'asking_to_withdraw']):  # чек кнопок
        if message.text == HELP_BUTTON_TEXT or message.text == '/help':
            await bot.send_message(user_id, text=HELP_MESSAGE_TEXT, parse_mode='Markdown')

        elif message.text == ADD_STRINGS_BUTTON_TEXT or message.text == '/add':
            update_user_flag(user_id, "adding_strings", True)
            await bot.send_message(user_id, text=ADD_STRINGS_MESSAGE_TEXT)

        elif message.text == PROCESS_BUTTON_TEXT or message.text == '/process':
            update_user_flag(user_id, 'changing_canvas', True)
            await bot.send_message(user_id, text=PROCESS_MESSAGE_TEXT)

        elif message.text == EXPLAIN_BUTTON_TEXT or message.text == '/explain':
            await bot.send_message(user_id, text=EXPLAIN_MESSAGE_TEXT)

        elif message.text == '/clear':
            handler.clear_user_available(message.chat.id)
            await bot.send_message(user_id, text=CLEAR_MESSAGE)

        else:
            await bot.send_message(user_id, text=BAD_COMMAND_MESSAGE_TEXT)

    elif message.text == '/stop' and not check_user_flag(message.chat.id, "adding_strings"):
        update_user_flag(message.chat.id, "changing_canvas", False)
        update_user_flag(message.chat.id, "asking_to_withdraw", False)
        update_user_flag(message.chat.id, "adding_strings", False)
        update_user_flag(message.chat.id, "adding_pic", False)
        await bot.send_message(user_id, text=PROCESSING_STOP_MESSAGE)

    elif check_user_flag(message.chat.id, "adding_strings"):
        if message.text == "/stop":
            await bot.send_message(message.chat.id, text=STOP_ADDING_MESSAGE)
            update_user_flag(message.chat.id, "adding_strings", False)
        else:
            loop = asyncio.get_running_loop()
            text_data = await loop.run_in_executor(None, strings_parsing, message.text)
            if text_data:
                for [i, j] in text_data:
                    handler.insert_available(message.chat.id, i, j)
                update_user_flag(message.chat.id, "adding_strings", False)
                await bot.send_message(message.chat.id, text=ADDED_MESSAGE)
            else:
                await bot.send_message(message.chat.id, text=WRONG_FORMAT_MESSAGE)


    elif check_user_flag(user_id, 'changing_canvas'):
        loop = asyncio.get_running_loop()
        text_data = await loop.run_in_executor(None, two_numbers_parsing, message.text)
        if text_data:
            await loop.run_in_executor(None, handler.update_canvas, message.chat.id, text_data[0], text_data[1])
            await bot.send_message(user_id, text=USE_STRINGS_MESSAGE)
            update_user_flag(user_id, 'changing_canvas', False)
            update_user_flag(user_id, 'asking_to_withdraw', True)
        else:
            await bot.send_message(user_id, text=WRONG_DATA_MESSAGE)


    elif check_user_flag(user_id, 'asking_to_withdraw'):
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, two_numbers_parsing, message.text)
        if len(data) == 2:
            alpha = int(data[0])
            if alpha < 0 or alpha > 1000:
                await bot.send_message(user_id, text=WRONG_ALPHA_MESSAGE)
            max_colors = int(data[1])
            if max_colors <= 0:
                await bot.send_message(user_id, text=WRONG_MAX_COLORS_MESSAGE)
            else:
                loop = asyncio.get_running_loop()
                await loop.run_in_executor(None, handler.update_params, message.chat.id, alpha, max_colors)
                await bot.send_message(user_id, text=SEND_NUDES_MESSAGE)
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
        params = handler.get_processing_params(message.chat.id)
        args = (image_path, pdf_path, message.chat.id, params[3], (params[0], params[1]), 1, params[2])
        loop = asyncio.get_running_loop()
        # noinspection PyTypeChecker
        await loop.run_in_executor(None, image_proc, *args)
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
