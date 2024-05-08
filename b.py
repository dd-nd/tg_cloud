from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import sqlite3 as sq
import telebot
import os

load_dotenv()
token = os.getenv("TOKEN")
bot = telebot.TeleBot(token)

files_to_update = {}  # Словарь для хранения названий файлов, требующих обновления

# Функция для проверки разрешенных типов файлов
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message: Message):
    bot.send_message( message.chat.id, 'Для загрузки просто отправьте файл 🤗')


# Обработчик приема документа от пользователя
@bot.message_handler(content_types=['document'])
def upload_file(message: Message):
    user_id = message.from_user.id
    user_nickname = message.from_user.username
    try:
        if allowed_file(message.document.file_name):
            file_name = secure_filename(message.document.file_name).split('.')[0]
            file_type = secure_filename(message.document.file_name).split('.')[1]
            downloaded_file = bot.download_file(bot.get_file(message.document.file_id).file_path)

            with sq.connect('db/database.db') as con: 
                cur = con.cursor()
                cur.execute(f'INSERT INTO files (name, format, data, user_id, user_name) VALUES (?, ?, ?, ?, ?)', (file_name, file_type, downloaded_file, 
                                                                                                                   user_id, user_nickname))
                bot.send_message( message.chat.id, 'Ням 🤗')
    except sq.IntegrityError:
        bot.send_message( message.chat.id, 'Попробуй еще раз 🥱')


# Обработчик вывода всех файлов пользователя 
@bot.message_handler(commands=['all'])
def get_file_name(message: Message):
    try:
        with sq.connect('db/database.db') as con: 
            cur = con.cursor()
            cur.execute(f'SELECT name FROM files WHERE user_id = "{message.from_user.id}"')
            results = [res[0] for res in cur.fetchall()]
        markup = InlineKeyboardMarkup()
        for i in results:
            btn = InlineKeyboardButton(i, callback_data=i)
            markup.add(btn)
        bot.send_message( message.chat.id, 'Выбери файл для дальнейших действий 🤗', reply_markup=markup)
    except Exception as e:
        bot.send_message( message.chat.id, f'Что-то пошло не так 🤗\n{str(e)}')


# Обработчик обновления названия файла
@bot.callback_query_handler(func=lambda call: True)
def edit_file_name(call: Message):
    bot.send_message(call.message.chat.id, 'Введите новое название 🤗')
    files_to_update[call.data] = call.from_user.id
    old_file_name = call.data

    # Функция для обработки текстового значения
    @bot.message_handler(func=lambda message: True)
    def handle_file_name(message: Message):
        new_file_name = message.text
        if call.from_user.id == files_to_update.get(call.data):
            try:
                with sq.connect('db/database.db') as con:
                    cur = con.cursor()
                    cur.execute(f'UPDATE files SET name = "{new_file_name}" WHERE user_id = "{call.from_user.id}" AND name = "{old_file_name}"')
                    con.commit()
                    bot.send_message(message.chat.id, 'Название файла успешно обновлено! ✨')
    
                    # Удаляем информацию о файле из словаря
                    del files_to_update[old_file_name]
            except Exception as e:
                bot.send_message(message.chat.id, f'Что-то пошло не так 🤗\n{str(e)}')
        else:
            bot.send_message(call.message.chat.id, 'У вас нет разрешения на изменение этого файла! ❌')
    bot.register_next_step_handler(call.message, handle_file_name)

# Обработчик обновления названия файла
# @bot.message_handler(content_types=['text'])
# def update_file_name(message):
#     if not message.text:
#         bot.send_message(message.chat.id, 'Пожалуйста, отправьте название файла текстом.')
#         return
#     user_id = message.from_user.id

#     if user_id == files_to_update['change']:
#         new_name = message.text

#         try:
#             with sq.connect('db/database.db') as con:
#                 cur = con.cursor()
#                 cur.execute(f'UPDATE files SET name = "{new_name}" WHERE user_id = "{user_id}" AND name = "{files_to_update[user_id]}"')
#                 con.commit()
#                 bot.send_message(message.chat.id, 'Название файла успешно обновлено!🎉')
#         except Exception as e:
#             bot.send_message(message.chat.id, f'Что-то пошло не так🤗\n{str(e)}')

#         # Удаляем информацию о файле из словаря
#         del files_to_update[user_id]


if __name__ == '__main__':
    bot.infinity_polling()