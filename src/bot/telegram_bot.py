import telebot
from telebot import types
from src.db.user_database_handler import UserGammaHandler
from parsing_data import strings_parsing, conv_parsing, get_rgb_by_gamma

handler = UserGammaHandler("../db/user_colors.sql")

TOKEN = 'YOUR_TOKEN'

bot = telebot.TeleBot(TOKEN)


def check_flags(user_id : str) -> bool:
    return True


def check_flag_adding_strings(user_id : str) -> bool:
    return True

def update_flag_adding_strings(user_id : str, to : bool) -> None:
    pass


def check_flag_adding_pic(user_id : str) -> bool:
    return True

def update_flag_adding_pic(user_id : str, to : bool) -> None:
    pass


def check_flag_changing_conv(user_id : str) -> bool:
    return True

def update_flag_changing_conv(user_id : str, to : bool) -> None:
    pass


def check_flag_asking_to_withdraw(user_id : str) -> bool:
    return True

def update_flag_asking_to_withdraw(user_id : str, to : bool) -> None:
    pass


@bot.message_handler(commands=['help', 'start'])
def command_handler(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    help_button = types.KeyboardButton("Памагите 🥺")
    add_strings_button = types.KeyboardButton("Добавить нитки 🐑")
    start_image_processing = types.KeyboardButton("Обработать изображение 🖼")
    explain = types.KeyboardButton("Ты кто такой 🧐")

    markup.add(help_button, add_strings_button, start_image_processing, explain)

    bot.send_message(message.chat.id, text="Здаров. Чего желаете?".format(message.from_user), reply_markup=markup)


@bot.message_handler(content_types=['text'])
def command_handler(message):
    if not check_flags(message.chat.id):
        if message.text == "Памагите 🥺":
            bot.send_message(message.chat.id, text=f'''
                                    Вот список команд, которые исполняются при нажатии на кнопки:\n

                                    -> Ты кто такой - краткий функционал бота, кто его породил на этот свет\n

                                    -> Добавить нитки - следующими сообщениями вы можете добавить нитки в формате: цвет - длина нитки в см.
                                       Для остановки пропишите /stop\n

                                    -> Баланс ниток - выводит имеющиеся нитки\n

                                    -> Обработать изображение - начало обработки изображения ботом.
                                       После нажатия бот попросит вас ввести изображение, размер канвы уровень детализации (кол-во цветов), 
                                       после чего выведет изображение, используемые нитки и места для и покупки, 
                                       если их нет или не хватает.

                                    ''')

        elif message.text == "Добавить нитки 🐑":
            update_flag_adding_strings(message.chat.id, True)
            bot.send_message(message.chat.id, text=f'''
                Добавь нитки в формате: цвет в HEX - длина в см.\n
                Можно добавлять сразу несколько, разделяй каждый ввод запятой, например:\n
                #ffffff - 157, #0000ff - 123
            ''')

        elif message.text == "Обработать изображение 🖼":
            update_flag_adding_pic(message.chat.id, True)
            bot.send_message(message.chat.id, text=f'''
                Начнем! Для начал сообщи мне размеры изображения. Введи кол-во клеток в длину и ширину одним сообщением через пробел.
            ''')

        elif message.text == "Ты кто такой 🧐":
            bot.send_message(message.chat.id, text=f'''
                *тут интродукшн бота кароче*
            ''')

        else:
            bot.send_message(message.chat.id, text=f'''
                Команда не найдена. Если вы забыли, какие команды есть - пропиши /help, для вызова кнопок пропиши /start
            ''')


    elif check_flag_adding_strings(message.chat.id):
        if message.text == "stop":
            bot.send_message(message.chat.id, text="Прекращаю добавлять цвета. Для кнопок снова пропишите /start")

            update_flag_adding_strings(message.chat.id, False)
        else:
            text_data = strings_parsing(message.text)
            if text_data:
                for [i, j] in text_data:
                    handler.insert(get_rgb_by_gamma(i), i)
                    continue
            else:
                bot.send_message(message.chat.id, text="Неправильный формат ввода! Если вы хотели прекратить ввод - пропишите /stop")


    elif check_flag_adding_pic(message.chat.id):
        #тут пикчу трахать
        bot.send_message(message.chat.id, text="Готово! Вам понадобится: *прописать нитки*")

        update_flag_adding_pic(message.chat.id, False)

    elif check_flag_changing_conv(message.chat.id):
        text_data = conv_parsing(message.text)
        if text_data:
            # приписать пользователю по айди длину и ширину картинки
            bot.send_message(message.chat.id,
                             text="Хорошо. Теперь скажите, хотите ли вы использовать свои нитки или только из новых?. Ответьте да или нет")

            update_flag_changing_conv(message.chat.id, False)
            update_flag_asking_to_withdraw(message.chat.id, True)
        else:
            bot.send_message(message.chat.id, text="Неправильный формат данных!")

    elif check_flag_asking_to_withdraw(message.chat.id):
        #запомнить выбор пользователя
        if message.text.lower() == "да":
            bot.send_message(message.chat.id, text="Хорошо, списываем. Отправьте фотографию")

            update_flag_asking_to_withdraw(message.chat.id, False)
            update_flag_adding_pic(message.chat.id, True)

        if message.text.lower() == "нет":
            bot.send_message(message.chat.id, text="Хорошо, не списываем. Отправьте фотографию")

            update_flag_asking_to_withdraw(message.chat.id, False)
            update_flag_adding_pic(message.chat.id, True)

        else:
            bot.send_message(message.chat.id, text="Неправильный формат ввода!")

    else:
        bot.send_message(message.chat.id, text="Это не команда! Чтобы ознакомиться со списком команд, пропишите /help")