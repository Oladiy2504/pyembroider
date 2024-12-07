import os

import telebot
from telebot import types
from src.db.user_database_handler import UserAvailableHandler
from src.bot.parsing_data import strings_parsing, conv_parsing, get_rgb_by_gamma
from src.util.image_processing import image_proc

handler = UserAvailableHandler("../db/user_colors.sql")

TOKEN = '7932733884:AAFsKDKeuFDvlbtue-jgf-bU2XKdMdzVgrM'

bot = telebot.TeleBot(TOKEN)

user_flags = {}
length = 100
width = 100

def update_user_flag(user_id, flag_name, state): # флаги для ввода ин-фы от юзера
    if user_id not in user_flags:
        user_flags[user_id] = {}
    user_flags[user_id][flag_name] = state

def check_user_flag(user_id, flag_name):
    return user_flags.get(user_id, {}).get(flag_name, False)


@bot.message_handler(commands=['start'])
def help_handler(message): # базовые кнопки
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    help_button = types.KeyboardButton("Памагите 🥺")
    add_strings_button = types.KeyboardButton("Добавить нитки 🐑")
    start_image_processing = types.KeyboardButton("Обработать изображение 🖼")
    explain = types.KeyboardButton("Ты кто такой 🧐")
    markup.add(help_button, add_strings_button, start_image_processing, explain)
    bot.send_message(message.chat.id, text="Здаров. Чего желаете?".format(message.from_user), reply_markup=markup)


@bot.message_handler(content_types=['text'])
def command_handler(message):
    user_id = message.chat.id

    if not any(check_user_flag(user_id, flag) for flag in ['adding_pic', 'changing_conv', 'adding_strings', 'asking_to_withdraw']): # чек кнопок
        if message.text == "Памагите 🥺":
            bot.send_message(user_id, text=f'''
                Вот список команд, которые исполняются при нажатии на кнопки:\n
                -> Ты кто такой - краткий функционал бота, кто его породил на этот свет\n
                -> Добавить нитки - добавь нитки в формате: цвет - длина нитки в см.\n
                -> Обработать изображение - начало обработки изображения ботом.\n
                -> Ты кто такой - информация о боте. \n
                
                Вот и все. А для кнопок пропиши /start.
            ''')

        elif message.text == "Добавить нитки 🐑":
            update_user_flag(user_id, "adding_strings", True)
            bot.send_message(user_id, text="Добавь нитки в формате: цвет в HEX - длина в см.")

        elif message.text == "Обработать изображение 🖼":
            update_user_flag(user_id, 'changing_conv', True)
            bot.send_message(user_id, text="Начнем! Введи кол-во клеток в длину и ширину через пробел.")

        elif message.text == "Ты кто такой 🧐":
            bot.send_message(user_id, text="Я бот, который помогает в работе с нитками и изображениями!")

        else:
            bot.send_message(user_id, text="Команда не найдена. Пропиши /help для получения списка команд.")


    elif check_user_flag(message.chat.id, "adding_strings"):
        if message.text == "stop":
            bot.send_message(message.chat.id, text="Прекращаю добавлять цвета. Для кнопок снова пропишите /start")
            update_user_flag(message.chat.id, "adding_strings", False)
        else:
            text_data = strings_parsing(message.text)
            if text_data:
                for [i, j] in text_data:
                    handler.insert(get_rgb_by_gamma(i), i)
                    continue
            else:
                bot.send_message(message.chat.id, text="Неправильный формат ввода! Если вы хотели прекратить ввод - пропишите /stop")


    elif check_user_flag(user_id, 'changing_conv'):
        text_data = conv_parsing(message.text)
        if text_data:
            global length, width
            length, width = text_data
            bot.send_message(user_id, text="Теперь скажите, хотите ли вы использовать свои нитки?")
            update_user_flag(user_id, 'changing_conv', False)
            update_user_flag(user_id, 'asking_to_withdraw', True)
        else:
            bot.send_message(user_id, text="Неправильный формат данных!")


    elif check_user_flag(user_id, 'asking_to_withdraw'):
        if message.text.lower() == "да":
            bot.send_message(user_id, text="Хорошо, списываем. Отправьте фотографию.")
            update_user_flag(user_id, 'asking_to_withdraw', False)
            update_user_flag(user_id, 'adding_pic', True)
        elif message.text.lower() == "нет":
            bot.send_message(user_id, text="Хорошо, не списываем. Отправьте фотографию.")
            update_user_flag(user_id, 'asking_to_withdraw', False)
            update_user_flag(user_id, 'adding_pic', True)
        else:
            bot.send_message(user_id, text="Неправильный формат ввода!")


    else:
        bot.send_message(user_id, text="Это не команда! Чтобы ознакомиться со списком команд, пропишите /help")


@bot.message_handler(content_types=['photo'])
def handle_image(message):
    if check_user_flag(message.chat.id, 'adding_pic'):
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image_path = f'received_image{message.chat.id}.jpg'
        pdf_path = f'output_image.pdf{message.chat.id}.pdf'
        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        image_proc(image_path, pdf_path)
        with open(pdf_path, 'rb') as pdf_file:
            bot.send_document(message.chat.id, pdf_file)
        os.remove(image_path)
        os.remove(pdf_path)
    else:
        bot.send_message(message.chat.id, text="Ну и нах ты мне это прислал? Яж не просил")


@bot.message_handler(func=lambda message: True)
def error_handler(message):
    bot.send_message(message.chat.id, text=f"Ой, кажется, вы что-то сделали не так! Вот подробная инструкция по использованию бота: https://youtu.be/dQw4w9WgXcQ?si=1DZGpDS1RDhs-ZJA")

bot.polling(none_stop=True, interval=0)