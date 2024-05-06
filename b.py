import telebot
from telebot.types import Message
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
            filename = secure_filename(message.document.file_name)
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with sq.connect('db/database.db') as con: 
                cur = con.cursor()
                cur.execute(f'INSERT INTO files (name, data, user_id, user_name) VALUES (?, ?, ?, ?)', (filename, downloaded_file, user_id, user_nickname))
                bot.send_message( message.chat.id, 'Схавал🤗')
    except sq.IntegrityError:
        bot.send_message( message.chat.id, 'Подавился🤗')

@bot.message_handler(commands=['all_names'])
def get_file_name(message: Message):
    user_id = message.from_user.id
    try:
        with sq.connect('db/database.db') as con: 
            cur = con.cursor()
            cur.execute(f'SELECT name FROM files WHERE user_id = "{user_id}"')
            bot.send_message( message.chat.id, cur.fetchall())
    except Exception as e:
        bot.send_message( message.chat.id, f'Что-то пошло не так🤗\n{str(e)}')


@bot.message_handler(commands=['change_name'])
def get_file_name(message: Message):
    user_id = message.from_user.id
    try:
        with sq.connect('db/database.db') as con: 
            cur = con.cursor()
            cur.execute(f'UPDATE files SET WHERE user_id = "{user_id}"')
            bot.send_message( message.chat.id, cur.fetchall())
    except Exception as e:
        bot.send_message( message.chat.id, f'Что-то пошло не так🤗\n{str(e)}')

if __name__ == '__main__':
    bot.polling()