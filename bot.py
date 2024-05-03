from telebot import types
import telebot
import sqlite3 as sq

bot = telebot.TeleBot('TOKEN')

def webAppKeyboard(): #создание клавиатуры с webapp кнопкой
   keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True) #создаем клавиатуру
   webAppAdd = types.WebAppInfo("https://telegram.mihailgok.ru") #создаем webappinfo - формат хранения url
   webAppEdit = types.WebAppInfo("https://games.mihailgok.ru") #создаем webappinfo - формат хранения url
   one_butt = types.KeyboardButton(text="Добавить", web_app=webAppAdd) #создаем кнопку типа webapp
   two_butt = types.KeyboardButton(text="Изменить", web_app=webAppEdit) #создаем кнопку типа webapp
   keyboard.add(one_butt, two_butt) #добавляем кнопки в клавиатуру

   return keyboard #возвращаем клавиатуру

# def webAppKeyboardInline():
#    keyboard = types.InlineKeyboardMarkup(row_width=1) #создаем клавиатуру inline
#    webApp = types.WebAppInfo("https://telegram.mihailgok.ru") #создаем webappinfo - формат хранения url
#    one = types.InlineKeyboardButton(text="Веб приложение", web_app=webApp) #создаем кнопку типа webapp
#    keyboard.add(one) #добавляем кнопку в клавиатуру

#    return keyboard #возвращаем клавиатуру


@bot.message_handler(commands=['start']) #обрабатываем команду старт
def start_fun(message):
    with sq.connect('db/database.db') as con: 
        cur = con.cursor()
        user_id = message.from_user.id
        user_nickname = message.from_user.username
        try:
            cur.execute(f'INSERT INTO users (id, name) VALUES ("{user_id}", "{user_nickname}")')
            bot.send_message( message.chat.id, 'Вы успешно зарегестрироны!\nМожете начинать наполнять свой список🤗', parse_mode="Markdown", reply_markup=webAppKeyboard())
        except sq.IntegrityError:
            bot.send_message( message.chat.id, 'Вы уже зарегестрироны!\nМожете наполнять свой список🤗', parse_mode="Markdown", reply_markup=webAppKeyboard())


@bot.message_handler(content_types="text")
def new_mes(message):
    bot.send_message( message.chat.id, 'Для пополнения списка нажмите "Добавить" и заполните нужные данные', parse_mode="Markdown", reply_markup=webAppKeyboard())


@bot.message_handler(content_types="web_app_data") #получаем отправленные данные 
def answer(webAppMes):
   print(webAppMes) #вся информация о сообщении
   print(webAppMes.web_app_data.data) #конкретно то что мы передали в бота
   bot.send_message(webAppMes.chat.id, f"получили инофрмацию из веб-приложения: {webAppMes.web_app_data.data}") 

if __name__ == '__main__':
   bot.infinity_polling()
