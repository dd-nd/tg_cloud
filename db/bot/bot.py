from telebot import types
import telebot
import sqlite3 as sq

bot = telebot.TeleBot('')

def webAppKeyboard(): 
   keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
   webAppAdd = types.WebAppInfo("https://telegram.mihailgok.ru") 
   webAppEdit = types.WebAppInfo("https://games.mihailgok.ru")
   one_butt = types.KeyboardButton(text="Добавить", web_app=webAppAdd) 
   two_butt = types.KeyboardButton(text="Изменить", web_app=webAppEdit)
   keyboard.add(one_butt, two_butt) 

   return keyboard

# def webAppKeyboardInline():
#    keyboard = types.InlineKeyboardMarkup(row_width=1)
#    webApp = types.WebAppInfo("https://telegram.mihailgok.ru")
#    one = types.InlineKeyboardButton(text="Веб приложение", web_app=webApp)
#    keyboard.add(one) 

#    return keyboard 


@bot.message_handler(commands=['start']) 
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


@bot.message_handler(content_types="web_app_data") 
def answer(webAppMes):
   print(webAppMes) 
   print(webAppMes.web_app_data.data)
   bot.send_message(webAppMes.chat.id, f"получили инофрмацию из веб-приложения: {webAppMes.web_app_data.data}") 


def starting():
    bot.infinity_polling()

if __name__ == '__main__':
    starting()