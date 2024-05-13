from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import sqlite3 as sq
import telebot
import os

load_dotenv()
token = os.getenv("TOKEN")
bot = telebot.TeleBot(token)

files_to_update = {}
actions = ["Download", "Edit name", "Delete"]

# Функция для проверки разрешенных типов файлов
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'mp4'}

# Обработчик команды /start
@bot.message_handler(commands=['start', 'help'])
def start(message: Message):
    bot.send_message( message.chat.id, 'Для загрузки просто отправьте файл 🤗\n📜 Общий список команд:\n\t\t' +
                     '/all - выбрать файл, посмотреть все файлы\n\t\t' +
                     '/edit - изменить выбранный файл\n\t\t' +
                     '/download - скачать выбранный файл\n\t\t' +
                     '/delete - удалить выбранный файл')


# Обработчик приема документа от пользователя
@bot.message_handler(content_types=['document', 'photo'])
def upload_file(message: Message):
    user_id = message.from_user.id
    user_nickname = message.from_user.username
    
    # Handling the document
    if message.document:
        try:
            if allowed_file(message.document.file_name):
                file_name = secure_filename(message.document.file_name).split('.')[0]
                file_type = secure_filename(message.document.file_name).split('.')[1]
                downloaded_file = bot.download_file(bot.get_file(message.document.file_id).file_path)
    
                with sq.connect('db/database.db') as con: 
                    cur = con.cursor()
                    cur.execute('INSERT INTO files (name, format, data, user_id, user_name) VALUES (?, ?, ?, ?, ?)',
                                (file_name, file_type, downloaded_file, user_id, user_nickname))
                    bot.send_message(message.chat.id, 'Ням 🤗')
            else:
                bot.send_message(message.chat.id, 'Этот файл не поддерживается 🥱')
        except sq.IntegrityError:
            bot.send_message(message.chat.id, 'Попробуй еще раз 🥱')
    
    # Handling the photo or video
    elif message.photo:
        try:
            photo = message.photo[-1]
            photo_id = photo.file_id
            photo = bot.download_file(bot.get_file(photo_id).file_path)

            file_path = bot.get_file(photo_id).file_path
            file_name, file_type = os.path.splitext(file_path)
            
            with sq.connect('db/database.db') as con: 
                cur = con.cursor()
                cur.execute('INSERT INTO files (name, format, data, user_id, user_name) VALUES (?, ?, ?, ?, ?)',
                            (file_name.split('/')[-1], file_type, photo, user_id, user_nickname))
                bot.send_message(message.chat.id, 'Ням 🤗')
        except sq.IntegrityError:
            bot.send_message(message.chat.id, 'Попробуй еще раз 🥱')

    elif message.video:
        try:
            video = message.video
            video_id = video.file_id
            video_data = bot.download_file(bot.get_file(video_id).file_path)

            file_path = bot.get_file(video_id).file_path
            file_name, file_type = os.path.splitext(file_path)

            with sq.connect('db/database.db') as con: 
                cur = con.cursor()
                cur.execute('INSERT INTO files (name, format, data, user_id, user_name) VALUES (?, ?, ?, ?, ?)',
                            (file_name.split('/')[-1], file_type, video_data, user_id, user_nickname))
                bot.send_message(message.chat.id, '🎥 Видео успешно загружено!')
        except sq.IntegrityError:
            bot.send_message(message.chat.id, 'Попробуй еще раз 🥱')


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
            btn = InlineKeyboardButton(i, callback_data=f'action_{i}')
            markup.add(btn)

        bot.send_message(message.chat.id, 'Выбери файл для дальнейших действий 🤗', reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, f'Что-то пошло не так 🤗\n{str(e)}')


# Обработчик обновления названия файла
@bot.callback_query_handler(func=lambda call: call.data.startswith('action_'))
def handle_file_actions(call: CallbackQuery):
    selected_file = call.data.split('_')[1:]
    selected_file = '_'.join(selected_file)
    markup = InlineKeyboardMarkup()
    
    for action in actions:
        btn = InlineKeyboardButton(action, callback_data=f'{action}_{selected_file}')
        markup.add(btn)
    
    bot.send_message(call.message.chat.id, f'Выбери действие для файла "{selected_file}" 🤗', reply_markup=markup)

files_to_update = {}  # Словарь для хранения названий файлов, требующих обновления

@bot.callback_query_handler(func=lambda call: any(action in call.data for action in actions))
def execute_file_action(call: CallbackQuery):
    action, selected_file = call.data.split('_')[0], call.data.split('_')[1:]
    selected_file = '_'.join(selected_file)

    files_to_update[selected_file] = call.from_user.id

    # Логика для скачивания файла
    if action == 'Download':
        if call.from_user.id == files_to_update.get(selected_file):
            try:
                with sq.connect('db/database.db') as con:
                    cur = con.cursor()
                    cur.execute(f"SELECT data, format FROM files WHERE user_id = {call.from_user.id} AND name = '{selected_file}'")
                    file_data, data_format = cur.fetchone()

                    bot.send_document(call.message.chat.id, file_data, visible_file_name=f'{selected_file}.{data_format}')
                        
                    del files_to_update[selected_file]
            except Exception as e:
                bot.send_message(call.message.chat.id, f'Что-то пошло не так 🤗\n{str(e)}')
        else:
            bot.send_message(call.message.chat.id, 'У вас нет разрешения на доступ к этому файлу! ❌')

    # Логика для изменения названия файла
    elif action == 'Edit name':
        bot.send_message(call.message.chat.id, 'Введите новое название 🤗')

        @bot.message_handler(func=lambda message: True)
        def handle_file_name(message: Message):
            new_file_name = message.text
            if call.from_user.id == files_to_update.get(selected_file):
                try:
                    with sq.connect('db/database.db') as con:
                        cur = con.cursor()
                        cur.execute(f'UPDATE files SET name = "{new_file_name}" WHERE user_id = "{call.from_user.id}" AND name = "{selected_file}"')
                        con.commit()
                        bot.send_message(message.chat.id, 'Название файла успешно обновлено! ✨')
                        del files_to_update[selected_file]
                except Exception as e:
                    bot.send_message(message.chat.id, f'Что-то пошло не так 🤗\n{str(e)}')
            else:
                bot.send_message(call.message.chat.id, 'У вас нет разрешения на изменение этого файла! ❌')
        bot.register_next_step_handler(call.message, handle_file_name)
    
    # Логика для удаления файла
    elif action == 'Delete':
        if call.from_user.id == files_to_update.get(selected_file):
            try:
                with sq.connect('db/database.db') as con:
                    cur = con.cursor()
                    cur.execute(f'DELETE FROM files WHERE user_id = "{call.from_user.id}" AND name = "{selected_file}"')
                    con.commit()
                    bot.send_message(call.message.chat.id, 'Файл успешно удален! 🥹')
                    del files_to_update[selected_file]
            except Exception as e:
                bot.send_message(call.message.chat.id, f'Что-то пошло не так 🤗\n{str(e)}')
        else:
            bot.send_message(call.message.chat.id, 'У вас нет разрешения на изменение этого файла! ❌')

if __name__ == '__main__':
    bot.infinity_polling()