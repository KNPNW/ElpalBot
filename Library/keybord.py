from telebot import types
import telebot
import sys
import os

workdir = os.getcwd()[:-7]
try:
    sys.path.insert(0, workdir+'Data')
    from setings import TOKEN, NAME_BD
except:
    workdir = "..\\"
    sys.path.insert(0, workdir+'Data')
    from setings import TOKEN, NAME_BD

try:
    from mysql_serv import MySQL
except:
    print("Произошла ошибка! Программа не работает!")


bot = telebot.TeleBot(TOKEN)


def menu(message, text):
    db = MySQL(NAME_BD)
    info = db.get_contract_info(db.get_contract_id(message.chat.id))

    menu_key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu_key.row("👤{}".format(info[1]))
    menu_key.row("Договор", "Бригада")
    menu_key.row("Фотоотчет", "Оставить отзыв")
    menu_key.row("Новый договор")
    menu_key.row("Поддержка")

    bot.send_message(message.chat.id, text, reply_markup=menu_key)


def feedback():
    feedback_key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    feedback_key.row("Отзыв о компании")
    feedback_key.row("Отзыв о бригаде")
    feedback_key.row("Назад")
    return feedback_key


def feedback_url(message):
    sites = types.InlineKeyboardMarkup()
    ian = types.InlineKeyboardButton(text='Яндекс', url='https://yandex.ru/profile/55512978791')
    google = types.InlineKeyboardButton(text='Google', url='https://clck.ru/QHszb')
    blizko = types.InlineKeyboardButton(text='Blizko', url='https://spb.blizko.ru/companies/14369395/reviews')
    twogis = types.InlineKeyboardButton(text='2GIS', url='https://go.2gis.com/4gr2b5')
    sites.add(ian)
    sites.add(google)
    sites.add(blizko)
    sites.add(twogis)

    bot.send_message(message.chat.id, "Пожалуйста, выберите сайт на котором хотите оставить Ваш отзыв.", reply_markup=sites)


def feedback_mark(message):
    key = types.InlineKeyboardMarkup()
    mark_1 = types.InlineKeyboardButton(text="1️⃣", callback_data="one")
    mark_2 = types.InlineKeyboardButton(text="2️⃣", callback_data="two")
    mark_3 = types.InlineKeyboardButton(text="3️⃣", callback_data="tree")
    mark_4 = types.InlineKeyboardButton(text="4️⃣", callback_data="four")
    mark_5 = types.InlineKeyboardButton(text="5️⃣", callback_data="five")
    mark_6 = types.InlineKeyboardButton(text="6️⃣", callback_data="six")
    mark_7 = types.InlineKeyboardButton(text="7️⃣", callback_data="second")
    mark_8 = types.InlineKeyboardButton(text="8️⃣", callback_data="eigth")
    mark_9 = types.InlineKeyboardButton(text="9️⃣", callback_data="nine")
    mark_10 = types.InlineKeyboardButton(text="🔟", callback_data="ten")
    key.add(mark_1, mark_2)
    key.add(mark_3, mark_4)
    key.add(mark_5, mark_6)
    key.add(mark_7, mark_8)
    key.add(mark_9, mark_10)

    bot.send_message(message.chat.id, "Оцените работу по\n10-ти бальной шкале", reply_markup=key)


def start_key():
    start = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start.row(types.KeyboardButton("Авторизация"))
    start.row(types.KeyboardButton("Поддержка"))
    return start


def list_obj(page, text, list, message):
    if len(list) == 1:
        contracts = types.InlineKeyboardMarkup()
        con_1 = types.InlineKeyboardButton(text="{}".format(list[page][0]), callback_data="{}".format(list[page][0]))
        con_2 = types.InlineKeyboardButton(text="{}".format(list[page][1]), callback_data="{}".format(list[page][1]))
        but_3 = types.InlineKeyboardButton(text="Закрыть", callback_data="cancel")
        contracts.add(con_1)
        contracts.add(con_2)
        contracts.add(but_3)
    elif page == 0:
        contracts = types.InlineKeyboardMarkup()
        con_1 = types.InlineKeyboardButton(text="{}".format(list[page][0]), callback_data="{}".format(list[page][0]))
        con_2 = types.InlineKeyboardButton(text="{}".format(list[page][1]), callback_data="{}".format(list[page][1]))
        but = types.InlineKeyboardButton(text="➡", callback_data="next")
        but_3 = types.InlineKeyboardButton(text="Закрыть", callback_data="cancel")
        contracts.add(con_1)
        contracts.add(con_2)
        contracts.add(but)
        contracts.add(but_3)
    elif page == len(list) - 1:
        contracts = types.InlineKeyboardMarkup()
        if len(list[page]) == 2:
            con_1 = types.InlineKeyboardButton(text="{}".format(list[page][0]),
                                               callback_data="{}".format(list[page][0]))
            con_2 = types.InlineKeyboardButton(text="{}".format(list[page][1]),
                                               callback_data="{}".format(list[page][1]))
            but = types.InlineKeyboardButton(text="⬅", callback_data="back")
            but_3 = types.InlineKeyboardButton(text="Закрыть", callback_data="cancel")
            contracts.add(con_1)
            contracts.add(con_2)
            contracts.add(but)
            contracts.add(but_3)
        else:
            con_1 = types.InlineKeyboardButton(text="{}".format(list[page][0]),
                                               callback_data="{}".format(list[page][0]))
            but = types.InlineKeyboardButton(text="⬅", callback_data="back")
            but_3 = types.InlineKeyboardButton(text="Закрыть", callback_data="cancel")
            contracts.add(con_1)
            contracts.add(but)
            contracts.add(but_3)

    else:
        contracts = types.InlineKeyboardMarkup()
        con_1 = types.InlineKeyboardButton(text="{}".format(list[page][0]), callback_data="{}".format(list[page][0]))
        con_2 = types.InlineKeyboardButton(text="{}".format(list[page][1]), callback_data="{}".format(list[page][1]))
        but_1 = types.InlineKeyboardButton(text="➡", callback_data="next")
        but_2 = types.InlineKeyboardButton(text="⬅", callback_data="back")
        but_3 = types.InlineKeyboardButton(text="Закрыть", callback_data="cancel")
        contracts.add(con_1)
        contracts.add(con_2)
        contracts.add(but_2, but_1)
        contracts.add(but_3)


    bot.send_message(message.chat.id, "{}".format(text), reply_markup=contracts)


def change_user_phone():
    start = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start.row(types.KeyboardButton("Вернуться в главное меню"))
    return start




