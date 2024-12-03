from io import BytesIO

import telebot
from PIL import Image
from telebot import types

TOKEN = 'YOUR_TOKEN'

bot = telebot.TeleBot(TOKEN)

def check_flags():
    return True

def check_flag_adding_string():
    return True

def check_flag_adding_pic():
    return True

def check_flag_changing_conv():
    return True

def check_flag_changing_scale():
    return True

def check_flag_asking_to_withdraw():
    return True

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
    if not check_flags():
        if message.text == "Памагите 🥺":
            bot.send_message(message.chat.id, text=f'''
                                    Вот список команд, которые исполняются при нажатии на кнопки:/n
                                    
                                    -> Ты кто такой - краткий функционал бота, кто его породил на этот свет/n
                                    
                                    -> Добавить нитки - следующими сообщениями вы можете добавить нитки в формате: цвет - длина нитки в см.
                                       Для остановки пропишите /stop/n
                                       
                                    -> Баланс ниток - выводит имеющиеся нитки/n
                                    
                                    -> Обработать изображение - начало обработки изображения ботом.
                                       После нажатия бот попросит вас ввести изображение, размер канвы уровень детализации (кол-во цветов), 
                                       после чего выведет изображение, используемые нитки и места для и покупки, 
                                       если их нет или не хватает.
                                       
                                    ''')

        elif message.text == "Добавить нитки 🐑":
            flag_adding_strings = True
            bot.send_message(message.chat.id, text=f'''
                Добавь нитки в формате: цвет в HEX - длина в см./n
                Можно добавлять сразу несколько, разделяй каждый ввод запятой, например:/n
                #ffffff - 157, #0000ff - 123
            ''')

        elif message.text == "Обработать изображение 🖼":
            flag_adding_scale = True
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
    elif check_flag_adding_string():
        #тут пропарсить сообщение и добавить к юзеру в таблицу цвет, длину
        pass

    elif check_flag_adding_pic():
        photo = message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        img = Image.open(BytesIO(downloaded_file))
        rotated_img = img.rotate(90, expand=True)  # пока тут rotate, когда появится преобразование в нужный формат - будет другое
        bio = BytesIO()
        bio.seek(0)
        rotated_img.save(bio, format="JPEG")
        bio.name = 'pixelated_image.jpg'
        bio.seek(0)
        bot.send_photo(message.chat.id, photo=bio)
        bot.send_message(message.chat.id, text="Готово! Вам понадобится: *прописать нитки*. Желаете ли вы использовать имеющиеся?")

    elif check_flag_changing_conv():
        #приписать пользователю по айди длину и ширину картинки
        bot.send_message(message.chat.id, text="Добавлен цвет и длина")
        pass

    elif check_flag_changing_scale():
        bot.send_message(message.chat.id, text="Добавлен размер клетки. Введите изображение")
        pass
        #приписать пользователю по айди размер 1 пикселя

    elif check_flag_asking_to_withdraw():
        bot.send_message(message.chat.id, text="хорошо, списываем")
        #спросить, списывать ли нитки пользователя