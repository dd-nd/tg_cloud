import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from werkzeug.utils import secure_filename
from io import BytesIO
# from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
import sqlite3 as sq
# Base = declarative_base()

# Функция для проверки разрешенных типов файлов
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Инициализация бота
bot = telebot.TeleBot("5594189828:AAE7yU8zVRNG4WGb30fe4GR9bZXmJV_A0HI")

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message: Message):
    bot.send_message( message.chat.id, 'Выбери файл для загрузки🤗')

# Обработчик приема документа от пользователя
@bot.message_handler(content_types=['document'])
def upload_file(message: Message):
    user_id = message.from_user.id
    user_nickname = message.from_user.username
    try:
        if allowed_file(message.document.file_name):
            file_name = secure_filename(message.document.file_name).split('.')[0]
            file_type = secure_filename(message.document.file_name).split('.')[1]
            # file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(bot.get_file(message.document.file_id).file_path)
            with sq.connect('db/database.db') as con: 
                cur = con.cursor()
                cur.execute(f'INSERT INTO files (name, format, data, user_id, user_name) VALUES (?, ?, ?, ?, ?)', (file_name, file_type, downloaded_file, 
                                                                                                                   user_id, user_nickname))
                bot.send_message( message.chat.id, 'Схавал🤗')
    except sq.IntegrityError:
        bot.send_message( message.chat.id, 'Подавился🤗')


# вывод всех файлов пользователя 
@bot.message_handler(commands=['my_files'])
def get_file_name(message: Message):
    user_id = message.from_user.id
    try:
        with sq.connect('db/database.db') as con: 
            cur = con.cursor()
            cur.execute(f'SELECT name FROM files WHERE user_id = "{user_id}"')
            results = [res[0] for res in cur.fetchall()]
        markup = InlineKeyboardMarkup()
        for i in results:
            btn = InlineKeyboardButton(i, callback_data=i)
            markup.add(btn)
        bot.send_message( message.chat.id, 'Выберите файл🤗', reply_markup=markup)
    except Exception as e:
        bot.send_message( message.chat.id, f'Что-то пошло не так🤗\n{str(e)}')

files_to_update = {}  # Словарь для хранения названий файлов, требующих обновления

# @bot.callback_query_handler(func=lambda call: True)
# def get_file_name(call: Message):
#     if call.data == "change":
#         bot.send_message( call.message.chat.id, 'Введите новое название🤗')
#         # Сохраняем информацию о файлах, требующих обновления
#         files_to_update[call.data] = call.from_user.id
#         print(files_to_update)

files_to_update = {}  # Словарь для хранения названий файлов, требующих обновления

# Обработчик обновления названия файла
@bot.callback_query_handler(func=lambda call: True)
def get_file_name(call: Message):
    bot.send_message(call.message.chat.id, 'Введите новое название🤗')
    files_to_update[call.data] = call.from_user.id
    old_file_name = call.data

    # Функция для обработки текстового значения
    @bot.message_handler(func=lambda message: True)
    def handle_file_name(message: Message):
        new_file_name = message.text
        if call.from_user.id == files_to_update.get(call.data):
            files_to_update[call.data] = new_file_name
            try:
                with sq.connect('db/database.db') as con:
                    cur = con.cursor()
                    cur.execute(f'UPDATE files SET name = "{new_file_name}" WHERE user_id = "{call.from_user.id}" AND name = "{old_file_name}"')
                    con.commit()
                    bot.send_message(message.chat.id, 'Название файла успешно обновлено!✨')
            except Exception as e:
                bot.send_message(message.chat.id, f'Что-то пошло не так🤗\n{str(e)}')
        else:
            bot.send_message(call.message.chat.id, 'У вас нет разрешения на изменение этого файла!❌')
    # Удаляем информацию о файле из словаря
    del files_to_update[call.from_user.id]
    bot.register_next_step_handler(call.message, handle_file_name)

# Обработчик обновления названия файла
@bot.message_handler(content_types=['text'])
def update_file_name(message):
    if not message.text:
        bot.send_message(message.chat.id, 'Пожалуйста, отправьте название файла текстом.')
        return
    user_id = message.from_user.id

    if user_id == files_to_update['change']:
        new_name = message.text

        try:
            with sq.connect('db/database.db') as con:
                cur = con.cursor()
                cur.execute(f'UPDATE files SET name = "{new_name}" WHERE user_id = "{user_id}" AND name = "{files_to_update[user_id]}"')
                con.commit()
                bot.send_message(message.chat.id, 'Название файла успешно обновлено!🎉')
        except Exception as e:
            bot.send_message(message.chat.id, f'Что-то пошло не так🤗\n{str(e)}')

        # Удаляем информацию о файле из словаря
        del files_to_update[user_id]



# # изменение названия
# @bot.message_handler(commands=['change'])
# def change_file_name(message: Message):
#     command_parts = message.html_text.split(' ')[1:]
#     print(command_parts)
#     user_id = message.from_user.id
#     try:
#         with sq.connect('db/database.db') as con: 
#             cur = con.cursor()
#             cur.execute(f'UPDATE files SET name = "{command_parts}" WHERE user_id = "{user_id}" AND name = "{command_parts[0]}"')
#             bot.send_message( message.chat.id, cur.fetchall())
#     except Exception as e:
#         bot.send_message( message.chat.id, f'Что-то пошло не так🤗\n{str(e)}')

if __name__ == '__main__':
    bot.infinity_polling()