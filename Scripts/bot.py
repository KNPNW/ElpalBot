from telebot import types
import telebot
import sys
import shutil
import os
import datetime
from threading import Timer

try:
    import Image
except ImportError:
    from PIL import Image


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

workdir = os.getcwd()[:-7]
try:
    sys.path.insert(0, workdir + 'Library')
    from mysql_serv import MySQL
    import authorization as auto
    import bitrix_data as bitrix
    import keybord as keybord
    import Google_drive as gd
except:
    workdir = "..\\"
    sys.path.insert(0, workdir + "Library")
    from mysql_serv import MySQL
    import authorization as auto
    import bitrix_data as bitrix
    import keybord as keybord
    import Google_drive as gd


try:
    sys.path.insert(0, workdir + 'Data')
    from setings import TOKEN, NAME_BD, folder_photo_bild, folder_objects, elpal_log
except:
    workDir = "..\\"
    sys.path.insert(0, workdir + 'Data')
    from setings import TOKEN, NAME_BD, folder_photo_bild, folder_objects, elpal_lod





@bot.message_handler(commands=['start'])
def welcome(message):
    db = MySQL(NAME_BD)
    if db.subscriber_exists(message.from_user.id):
        db.delete_user(message.from_user.id)
    start = keybord.start_key()
    bot.send_message(message.chat.id, "Добро пожаловать, {0.first_name}!\n"
                                      "Давайте знакомиться!".format(message.from_user, bot.get_me()),
                                       parse_mode='html', reply_markup=start)


@bot.message_handler(content_types=['text'])
def treatment(message):
    if message.chat.type == 'private':
        db = MySQL(NAME_BD)
        if db.auto_chek(message.from_user.id) and len(str(db.get_contract_id(message.from_user.id))) > 4:
            if message.text == "Договор":
                button_contract(message)
            elif message.text == "Новый договор":
                db.delete_user(message.from_user.id)
                start = types.ReplyKeyboardRemove()
                phone = bot.send_message(message.chat.id, "*Введите номер телефона на который зарегистрирован договор*\n"
                                                          "Пример: 88122411575\n\n"
                                                          "Если возникли вопросы обратитесь в поддержку компании +7(812)241-15-75", reply_markup=start, parse_mode="Markdown")
                bot.register_next_step_handler(phone, phone_in_base)
            elif message.text == "Бригада":
                button_brigade(message)
            elif message.text == "Поддержка":
                bot.send_message(message.chat.id, "Проблеммы с ботом - @nezinsk\n"
                                                  "Проблемы с обьектом - @Norbee\n"
                                                  "Горячая линиия - +7(812)241-15-75")
            elif message.text == "Оставить отзыв":
                db.update_stage(message.chat.id, "feedback")
                button_feedback(message)
            elif message.text[0] == "👤":
                pass
            elif message.text == "Фотоотчет":
                button_photos(message)
            else:
                stage = db.get_stage(message.chat.id)
                if stage == "feedback":
                     feedback_choose(message)
                elif stage == "choose":
                    next_step(message)
                else:
                    keybord.menu(message, "Неизвестная команда!")
        else:
            if message.text == "Поддержка":
                bot.send_message(message.chat.id, "Проблеммы с ботом - @nezinsk\n"
                                                  "Проблемы с обьектом - @Norbee\n"
                                                  "Горячая линиия - +7(812)241-15-75")
            elif message.text == "Авторизация":
                start = types.ReplyKeyboardRemove()
                phone = bot.send_message(message.chat.id, "*Введите номер телефона на который зарегистрирован договор*\n"
                                                          "Пример: 88122411575\n\n"
                                                          "Если возникли вопросы обратитесь в поддержку компании +7(812)241-15-75", reply_markup=start, parse_mode="Markdown")
                bot.register_next_step_handler(phone, phone_in_base)
            else:
                start = keybord.start_key()
                bot.send_message(message.chat.id, "Неизвестная команда!", reply_markup=start)


def phone_in_base(message):
    if message.text.isdigit():
        db = MySQL(NAME_BD)
        contract_id_with_phone = db.phone_exists(message.text)
        if bool(len(contract_id_with_phone)):
            if len(contract_id_with_phone) == 1:
                auto.auto_main(message, contract_id_with_phone[0])
                password = bot.send_message(message.chat.id, "Введите пароль🔑:")
                bot.register_next_step_handler(password, password_login)
            else:
                choose_contract(contract_id_with_phone)
                contracts = keybord.list_obj(page, "Первая страница", list_contract, message)
                bot.send_message(message.chat.id, "На Ваш номер привязано несколько договоров.\nВыбереите необходимый",
                                 reply_markup=contracts)
        else:
            new_phone = bot.send_message(message.chat.id, "*На данный номер телефона не зарегистрированно ни одного договора!*\n\n"
                                                          "Повторите ввод.", parse_mode="Markdown")
            bot.register_next_step_handler(new_phone, phone_in_base)


def choose_contract(data):
    global page, list_contract
    page = 0
    list_contract = data

    if len(data) // 2 > 0:
        kol = len(data) // 2
        j = 0
        list_contract = []
        for i in range(0, kol):
            bloc = [data[j], data[j + 1]]
            j += 2
            list_contract.append(bloc)
        if len(data) % 2 == 1:
            list_contract.append([data[j]])
    else:
        list_contract.append([data[0]])



def password_login(message):
    password_db = MySQL(NAME_BD)
    if password_db.password_chek(message.chat.id, ('"' + message.text + '"')):
        password_db.update_reg(message.chat.id, True)
        keybord.menu(message, "Авторизация выполнена!")
        bot.send_message(elpal_log, "Авторизация по договору {} выполнена!".format(password_db.get_contract_id(message.chat.id)))
    else:
        if message.text == 'Вернуться в главное меню':
            start = keybord.start_key()
            bot.send_message(message.chat.id, "Вы вернулись в главное меню!", reply_markup=start)
        else:
            main_menu = keybord.change_user_phone()
            input_pass = bot.send_message(message.chat.id, "Пароль неверный! Попробуйте еще раз!", reply_markup=main_menu)
            bot.register_next_step_handler(input_pass, password_login)


def button_contract(message):
    db = MySQL(NAME_BD)
    contract_id = db.get_contract_id(message.chat.id)
    info = db.get_contract_info(contract_id)
    info = list(map(str, info))
    if info[2] == '0':
        info[2] = 'Не назначена'
    if info[3] == '0':
        info[3] = 'Не назначена'
    bot.send_message(message.chat.id, "*Договор №* - {}\n"
                                      "*Менеджер* - {}\n"
                                      "*Бригада* -️ {}\n"
                                      "*Начало строительства* -️ {}\n".
                     format(info[0], info[4], info[2], info[3]), parse_mode="Markdown")
    try:
        have_data = bitrix.file_from_bitrix(info[0], message.chat.id)
        if have_data == 1:
            Dir_files = workdir + "/Output/cache/" + str(message.chat.id)
            try:
                files = os.listdir(Dir_files)
                bot.send_message(message.chat.id, "Ваши документы:")
                for file in files:
                    doc = open(Dir_files + "/" + str(file), 'rb')
                    bot.send_document(message.chat.id, doc)
            except:
                pass
    except:
        pass


def button_feedback(message):
    feedback_key = keybord.feedback()

    chose = bot.send_message(message.chat.id, "*Выберите тип отзыва:*", reply_markup=feedback_key, parse_mode="Markdown")
    bot.register_next_step_handler(chose, feedback_choose)


def feedback_choose(message):
    if message.text == "Отзыв о бригаде":
        feedback_brigade(message)
    elif message.text == "Отзыв о компании":
        keybord.feedback_url(message)
        keybord.menu(message, "Спасибо, Ваш отзыв очень важен!")
    else:
        if message.text == 'Назад':
            keybord.menu(message, "Вы вернулись в главное меню.")
        else:
            choose = bot.send_message(message.chat.id, "Неизвестная команда!")
            bot.register_next_step_handler(choose, feedback_choose)



def feedback_brigade(message):
    db = MySQL(NAME_BD)
    contract_id = db.get_contract_id(message.from_user.id)
    if db.det_number_brigade(contract_id) != '0':
        if not db.get_availability_feedback(contract_id):
            delit_key = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, "Пожалуйста, оцените работу Вашей бригады по 10-ти бальной шкале.", reply_markup=delit_key)
            keybord.feedback_mark(message)
        else:
            db.update_stage(message.chat.id, "choose")
            choose_key = types.ReplyKeyboardMarkup(resize_keyboard=True)
            choose_key.row("Изменить")
            choose_key.row("Назад️")
            choose = bot.send_message(message.chat.id, "У вас уже есть оставленный отзыв", reply_markup=choose_key)
            bot.register_next_step_handler(choose, next_step)
    else:
        choose = bot.send_message(message.chat.id, "К сожалению, бригада еще не назначена!")
        bot.register_next_step_handler(choose, feedback_choose)


def next_step(messagee):
    db = MySQL(NAME_BD)
    if messagee.text == "Изменить":
        contract_id = db.get_contract_id(messagee.from_user.id)
        db.delete_feedback(contract_id)
        delit_key = types.ReplyKeyboardRemove()
        bot.send_message(messagee.chat.id, "Предыдуший отзыв был удален!", reply_markup=delit_key)
        keybord.feedback_mark(messagee)
    else:
        button_feedback(messagee)


@bot.callback_query_handler(func=lambda c: True)
def inlin(c):
    global page, list_contract

    marks = {'one': 1, 'two': 2, 'tree': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eigth': 8, 'nine': 9, 'ten': 10}
    if c.data in marks:
        db = MySQL(NAME_BD)
        contract_id = db.get_contract_id(c.message.chat.id)
        db.update_feedback(True, marks[c.data], contract_id)
        bot.send_message(elpal_log, "Оценка бригады по договру {} - {}".format(contract_id, marks[c.data]))
        bot.delete_message(c.message.chat.id, c.message.message_id)
        msg = bot.send_message(c.message.chat.id, 'Спасибо, если не сложно напишите отзыв о бригаде *одним сообщением*',
                               parse_mode="Markdown")
        bot.register_next_step_handler(msg, feedback)
    elif c.data == "next":
        page += 1
        bot.delete_message(c.message.chat.id, c.message.message_id)
        keybord.list_obj(page, "Следующая страница:", list_contract, c.message)
    elif c.data == "back":
        page -= 1
        bot.delete_message(c.message.chat.id, c.message.message_id)
        keybord.list_obj(page, "Предыдущая страница:", list_contract, c.message)
    elif c.data == "cancel":
        bot.delete_message(c.message.chat.id, c.message.message_id)
        start = keybord.start_key()
        bot.send_message(c.message.chat.id, "Авторизация прервана!", reply_markup=start)
    elif len(c.data) > 4 and c.data.isdigit():
        db = MySQL(NAME_BD)
        auto.auto_main(c.message, c.data, db.get_phone_throw_id(c.data))
        bot.delete_message(c.message.chat.id, c.message.message_id)
        password = bot.send_message(c.message.chat.id, "Введите пароль🔑:")
        bot.register_next_step_handler(password, password_login)


def feedback(message):
    db_feed = MySQL(NAME_BD)
    contract_id = db_feed.get_contract_id(message.chat.id)
    feet_text = open(workdir + "/Output/cache/{}/{}.txt".format(message.chat.id, str(contract_id)), 'w')
    feet_text.write(message.text)
    feet_text.close()
    db_feed.update_stage(message.chat.id, "None")
    keybord.menu(message, "Спасибо, Ваш отзыв очень важен!")
    bot.send_message(elpal_log, "Отзыв по договору {}:\n{}".format(contract_id, message.text))
    gd.add_feedback(str(contract_id), message.chat.id, 'Feedbacks')


def button_new_contract(message):
    global autoriz
    autoriz = False
    support = types.ReplyKeyboardMarkup(resize_keyboard=True)
    support.add(types.KeyboardButton("Поддержка"))
    phone = bot.send_message(message.chat.id, "Введите номер телефона, на который привязан договор.\nПример: 88122411575", reply_markup=support)
    bot.register_next_step_handler(phone, phone_in_base)


def button_brigade(message):
    db = MySQL(NAME_BD)
    contract_id = db.get_contract_id(message.chat.id)
    brigade_num = db.det_number_brigade(contract_id)
    if brigade_num != '0':
        bild_info = db.get_brigade_names("'"+brigade_num+"'")
        names = list(map(str, bild_info[0]))
        photo_id = list(map(str, bild_info[1]))
        phone = list(map(str, bild_info[2]))
        if len(names) > 0:
            for i in range(len(names)):
                names[i] = names[i].translate(str.maketrans('', '', "\/:()*''?[],<>|"))
                photo_id[i] = photo_id[i].translate(str.maketrans('', '', "\/:()*''?[],<>|"))
                phone[i] = phone[i].translate(str.maketrans('', '', "\/:''()?[],<>|"))
            try:
                bot.send_message(message.chat.id, "*Ваша бригада:*\n"
                                                  "Загрузка данных может занять некоторое время", parse_mode="Markdown")
                gd.get_bilds_photo(folder_photo_bild, photo_id, message.chat.id)

                for i in range(len(names)):
                    bot.send_message(message.chat.id, "*{}*\nТелефон - {}".format(names[i],
                                                                                        phone[i][:1] + " (" + phone[i][1:4] + ") " +
                                                                                        phone[i][4:7] + "-" + phone[i][7:9] + "-" +
                                                                                        phone[i][9:]), parse_mode="Markdown")
                    try:
                        photo = open(workdir + "Output/cache/{}/".format(message.chat.id) + str(photo_id[i]) + ".jpeg", 'rb')
                        bot.send_photo(message.chat.id, photo)
                    except:
                        bot.send_message(message.chat.id, "К сожалению, фотография не загружена!")
            except:
                pass
        else:
            bot.send_message(message.chat.id, "К сожалению, данные о вашей бригаде не добавлены!\n"
                                              "Пожалуйста, обратитесь в поддержку!")
    else:
        bot.send_message(message.chat.id, "Бригада не назначена!")



def button_photos(message):

    bot.send_message(message.chat.id, "*Фотоотчёт:*\nЗагрузка данных может занять некоторое время", parse_mode="Markdown")
    db = MySQL(NAME_BD)
    contract_id = db.get_contract_id(message.chat.id)
    try:
        if gd.get_obj_photos(folder_objects, str(contract_id), message.chat.id) != '0':
            files = os.listdir(workdir + "Output/cache/{}/".format(message.chat.id))
            for file in files:
                photo = open(workdir + "Output/cache/{}/".format(message.chat.id) + file, 'rb')
                bot.send_photo(message.chat.id, photo)
        else:
            bot.send_message(message.chat.id, "К сожалению, бригада пока не загрузила фотографии.")
    except:
        bot.send_message(message.chat.id, "К сожалению, бригада пока не загрузила фотографии.")


def delete_cache():
    files = os.listdir(workdir + "Output/cache/")
    for f in files:
        try:
            shutil.rmtree(workdir + "Output/cache/{}".format(f))
        except:
            os.remove(workdir + "Output/cache/{}".format(f))


rt = RepeatedTimer(86400, delete_cache)
bot.polling(none_stop=True)

