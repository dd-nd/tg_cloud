from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import sqlite3 as sq
import telebot

actions = ["Download", "Edit name", "Delete"]

bot = telebot.TeleBot('6311871616:AAH1OYnplmeNTGwpraw1okWcPcn77sgwG4U')
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
    selected_file = call.data.split('_')[1]
    markup = InlineKeyboardMarkup()
    
    for action in actions:
        btn = InlineKeyboardButton(action, callback_data=f'{action}_{selected_file}')
        markup.add(btn)
    
    bot.send_message(call.message.chat.id, f'Выбери действие для файла "{selected_file}" 🤗', reply_markup=markup)

files_to_update = {}  # Словарь для хранения названий файлов, требующих обновления

@bot.callback_query_handler(func=lambda call: any(action in call.data for action in actions))
def execute_file_action(call: CallbackQuery):
    action, selected_file = call.data.split('_')[0], call.data.split('_')[1]

    if action == 'Download':
        # Логика для скачивания файла
        bot.send_message(call.message.chat.id, f'Вы выбрали действие "Скачать" для файла "{selected_file}" 📥')
    
    elif action == 'Edit name':
        bot.send_message(call.message.chat.id, 'Введите новое название 🤗')
        files_to_update[selected_file] = call.from_user.id
    
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
    
    elif action == 'Delete':
        # Логика для удаления файла
        bot.send_message(call.message.chat.id, f'Вы выбрали действие "Удалить" для файла "{selected_file}" ❌')

if __name__ == '__main__':
    bot.infinity_polling()