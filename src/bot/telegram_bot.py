import asyncio
import os
from telebot import types
from telebot.async_telebot import AsyncTeleBot

from src.db.user_database_handler import UserDatabaseHandler
from src.bot.parsing_data import strings_parsing, conv_parsing
from src.util.image_processing import image_proc

flags = {'adding_pic': -1, 'changing_conv': -2, 'adding_strings': -3, 'asking_to_withdraw': -4}

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
    help_button = types.KeyboardButton("Памагите 🥺")
    add_strings_button = types.KeyboardButton("Добавить нитки 🐑")
    start_image_processing = types.KeyboardButton("Обработать изображение 🖼")
    explain = types.KeyboardButton("Ты кто такой 🧐")
    markup.add(help_button, add_strings_button, start_image_processing, explain)
    await bot.send_message(message.chat.id, text="Здаров. Чего желаете?".format(message.from_user), reply_markup=markup)


@bot.message_handler(content_types=['text'])
async def command_handler(message):
    user_id = message.chat.id

    if not any(check_user_flag(user_id, flag) for flag in
               ['adding_pic', 'changing_conv', 'adding_strings', 'asking_to_withdraw']):  # чек кнопок
        if message.text == "Памагите 🥺":
            await bot.send_message(user_id, text=f'''
                Вот список команд, которые исполняются при нажатии на кнопки:\n
                -> Ты кто такой - краткий функционал бота, кто его породил на этот свет\n
                -> Добавить нитки - добавь нитки в формате: цвет - длина нитки в см.\n
                -> Обработать изображение - начало обработки изображения ботом.\n
                -> Ты кто такой - информация о боте. \n
                
                Вот и все. А для кнопок пропиши /start.
            ''')

        elif message.text == "Добавить нитки 🐑":
            update_user_flag(user_id, "adding_strings", True)
            await bot.send_message(user_id, text="Добавь нитки в формате: цвет в HEX - длина в см.")

        elif message.text == "Обработать изображение 🖼":
            update_user_flag(user_id, 'changing_conv', True)
            await bot.send_message(user_id, text="Начнем! Введи кол-во клеток в длину и ширину через пробел.")

        elif message.text == "Ты кто такой 🧐":
            await bot.send_message(user_id, text="Я бот, который помогает в работе с нитками и изображениями!")

        else:
            await bot.send_message(user_id, text="Команда не найдена. Пропиши /help для получения списка команд.")

    elif message.text == '/stop' and not check_user_flag(message.chat.id, "adding_strings"):
        update_user_flag(message.chat.id, "changing_conv", False)
        update_user_flag(message.chat.id, "asking_to_withdraw", False)
        update_user_flag(message.chat.id, "adding_strings", False)
        update_user_flag(message.chat.id, "adding_pic", False)
        await bot.send_message(user_id, text="ну и ладно... не очень-то и хотелось...")

    elif check_user_flag(message.chat.id, "adding_strings"):
        if message.text == "/stop":
            await bot.send_message(message.chat.id, text="Прекращаю добавлять цвета")
            update_user_flag(message.chat.id, "adding_strings", False)
        else:
            text_data = strings_parsing(message.text)
            if text_data:
                for [i, j] in text_data:
                    # handler.insert(get_rgb_by_gamma(i), i)
                    continue
            else:
                await bot.send_message(message.chat.id,
                                       text="Неправильный формат ввода! Если вы хотели прекратить ввод - пропишите /stop")


    elif check_user_flag(user_id, 'changing_conv'):
        text_data = conv_parsing(message.text)
        if text_data:
            global length, width
            length, width = text_data
            await bot.send_message(user_id, text="Теперь скажите, хотите ли вы использовать свои нитки?")
            update_user_flag(user_id, 'changing_conv', False)
            update_user_flag(user_id, 'asking_to_withdraw', True)
        else:
            await bot.send_message(user_id, text="Неправильный формат данных!")


    elif check_user_flag(user_id, 'asking_to_withdraw'):
        if message.text.lower() == "да":
            await bot.send_message(user_id, text="Хорошо, списываем. Отправьте фотографию.")
            update_user_flag(user_id, 'asking_to_withdraw', False)
            update_user_flag(user_id, 'adding_pic', True)
        elif message.text.lower() == "нет":
            await bot.send_message(user_id, text="Хорошо, не списываем. Отправьте фотографию.")
            update_user_flag(user_id, 'asking_to_withdraw', False)
            update_user_flag(user_id, 'adding_pic', True)
        else:
            await bot.send_message(user_id, text="Неправильный формат ввода!")


    else:
        await bot.send_message(user_id, text="Это не команда! Чтобы ознакомиться со списком команд, пропишите /help")


@bot.message_handler(content_types=['photo'])
async def handle_image(message):
    if check_user_flag(message.chat.id, 'adding_pic'):
        file_info = await bot.get_file(message.photo[-1].file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        image_path = f'received_image{message.chat.id}.jpg'
        pdf_path = f'output_image.pdf{message.chat.id}.pdf'
        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        image_proc(image_path, pdf_path, message.chat.id)
        with open(pdf_path, 'rb') as pdf_file:
            await bot.send_document(message.chat.id, pdf_file)
        os.remove(image_path)
        os.remove(pdf_path)
        update_user_flag(message.chat.id, 'adding_pic', False)
        await bot.send_message(message.chat.id, text="Готово!")
    else:
        await bot.send_message(message.chat.id, text="Ну и нах ты мне это прислал? Яж не просил")


@bot.message_handler(func=lambda message: True)
async def error_handler(message):
    await bot.send_message(message.chat.id,
                           text=f"Ой, кажется, вы что-то сделали не так! Вот подробная инструкция по использованию бота: https://youtu.be/dQw4w9WgXcQ?si=1DZGpDS1RDhs-ZJA")


asyncio.run(bot.infinity_polling())
