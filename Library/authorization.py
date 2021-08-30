import telebot
import random
import sys
import os

workdir = os.getcwd()[:-7]
try:
    sys.path.insert(0, workdir+'Data')
    from setings import PASS
except:
    workdir = "..\\"
    sys.path.insert(0, workdir+'Data')
    from setings import PASS

try:
    from smsc_api import SMSC
    from mysql_serv import MySQL
    from setings import TOKEN, NAME_BD
except:
    print("Произошла ошибка! Программа не работает!")

smsc = SMSC()
bot = telebot.TeleBot(TOKEN)


def generarion_pass():
    return ''.join(
        [random.choice(list('1234567890')) for x in range(4)])


def auto_main(message, contract_id, phone=0):
    database = MySQL(NAME_BD)
    password = generarion_pass()
    if phone == 0:
        phone = message.text
    if database.subscriber_exists(message.chat.id):
        database.update_subscription(message.chat.id, contract_id, ('"' + password + '"'), False)
        smsc.send_sms(phone, "Ваш пароль: {}".format(password), sender='ELKI-PALKI')
    else:
        database.add_subscriber(message.chat.id, contract_id, ('"' + password + '"'))
        smsc.send_sms(phone, "Ваш пароль: {}".format(password), sender='ELKI-PALKI')

