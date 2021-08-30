import pymysql.cursors
import sys
import os

workdir = os.getcwd()[:-7]

try:
    sys.path.insert(0, workdir+'Data')
    from setings import PASS, NAME_BD, NAME_HOST
except:
    workdir = "..\\"
    sys.path.insert(0, workdir+'Data')
    from setings import PASS, NAME_BD, NAME_HOST


class MySQL:
    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = pymysql.connect(host=NAME_HOST,
                                          user=NAME_BD,
                                          password=PASS,
                                          db=database,
                                          charset='utf8mb4',
                                          autocommit=True)
        self.cursor = self.connection.cursor()

    def subscriber_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        self.cursor.execute("""SELECT * FROM user_info WHERE user_id = {};""".format(user_id))
        result = self.cursor.fetchall()
        return bool(len(result))

    def delete_user(self, user_id):
        return self.cursor.execute("""DELETE FROM user_info WHERE user_id = {}""".format(user_id))

    def add_subscriber(self, user_id, contract_id, password):
        """Добавляем нового подписчика"""
        self.cursor.execute("INSERT INTO user_info (user_id, contract_id, password) VALUES({}, {}, {});".format(user_id, contract_id, password))
        self.connection.commit()

    def auto_chek(self, user_id):
        self.cursor.execute(
            """SELECT * FROM user_info WHERE user_id = {} AND reg = TRUE;""".format(user_id))
        result = self.cursor.fetchall()
        return bool(len(result))

    def password_chek(self, user_id, password):
        self.cursor.execute("""SELECT * FROM user_info WHERE user_id = {} AND password = {};""".format(user_id, password))
        result = self.cursor.fetchall()
        return bool(len(result))

    def contract_exists(self, contract_id):
        """Проверяем, есть ли уже юзер в базе"""
        self.cursor.execute("""SELECT * FROM contract_info WHERE contract_id = {}""".format(contract_id))
        result = self.cursor.fetchall()
        return bool(len(result))

    def contract_id_exist(self, contract_id):
        self.cursor.execute(
            """SELECT * FROM contract_info WHERE contract_id = {};""".format(contract_id))
        result = self.cursor.fetchall()
        return bool(len(result))

    def update_subscription(self, user_id, contract_id, password, reg):
        """Обновляем статус подписки пользователя"""
        self.cursor.execute(
            """UPDATE user_info SET contract_id = {}  WHERE user_id = {}""".format(contract_id, user_id))
        self.cursor.execute(
            """UPDATE user_info SET password = {}  WHERE user_id = {}""".format(str(password), user_id))
        self.cursor.execute(
            """UPDATE user_info SET reg = {} WHERE user_id = {}""".format(reg, user_id))

    def get_contract_id(self, user_id):
        """    """
        self.cursor.execute("SELECT contract_id FROM user_info WHERE user_id = {};".format(user_id))
        result = (self.cursor.fetchall()[0])[-1]
        return result

    def get_contract_info(self, contract_id):
        """ """
        result = []
        atrs = ['contract_id', 'FIO_order', 'num_bragade', 'date_bild', 'FIO_meneg']
        for atr in atrs:
            self.cursor.execute("SELECT {} FROM contract_info WHERE contract_id = {}".format(atr, contract_id))
            promeg = (self.cursor.fetchall()[0])[-1]
            result.append(promeg)
        return result


    def get_brigade_names(self, num_brigade):
        """ """
        self.cursor.execute("SELECT FIO_bild FROM brigade_info WHERE num_brigade = {};".format(num_brigade))
        names = self.cursor.fetchall()
        self.cursor.execute("SELECT bild_id FROM brigade_info WHERE num_brigade = {};".format(num_brigade))
        id = self.cursor.fetchall()
        self.cursor.execute("SELECT phone_bild FROM brigade_info WHERE num_brigade = {};".format(num_brigade))
        phone = self.cursor.fetchall()
        return [names, id, phone]

    def det_number_brigade(self, contract_id):
        """ """
        self.cursor.execute("""SELECT num_bragade FROM contract_info WHERE contract_id = {}""".format(contract_id))
        result = (self.cursor.fetchall()[0])[-1]
        return result

    def get_phone_throw_id(self, id):
        self.cursor.execute("""SELECT phone_order FROM contract_info WHERE contract_id = {}""".format(id))
        result = (self.cursor.fetchall()[0])[-1]
        return result

    def update_reg(self, user_id, reg):
        self.cursor.execute(
            """UPDATE user_info SET reg = {} WHERE user_id = {}""".format(reg, user_id))

    def get_brigade_photo_id(self, names):
        """ """
        result = []
        for name in names:
            self.cursor.execute("SELECT bild_id FROM brigade_info WHERE FIO_bild = %s;" % name )
            promeg = self.cursor.fetchall()
            result.append(promeg)
        return result

    def get_availability_feedback(self, contract_id):
        self.cursor.execute("""SELECT * FROM feedback WHERE availability = {} AND contract_id = {};""".format('True', contract_id))
        result = self.cursor.fetchall()
        return bool(len(result))

    def update_feedback(self, avail, mark, contract_id):
        """Обновляем статус отзыва"""
        return self.cursor.execute(
            """INSERT INTO feedback (contract_id, availability, mark) VALUES ({}, {}, {});""".format(contract_id, avail, mark))

    def phone_exists(self, phone):
        """Проверяем, есть ли уже юзер в базе"""
        self.cursor.execute("""SELECT contract_id FROM contract_info WHERE phone_order = {}""".format(phone))
        result = self.cursor.fetchall()
        result = list(map(str, result))
        for i in range(len(result)):
            result[i] = result[i].translate(str.maketrans('', '', "\/:()*''?[],<>|"))
        return result


    def delete_feedback(self, id):
        return self.cursor.execute("""DELETE FROM feedback WHERE contract_id = {}""".format(id))

    def get_stage(self, user_id):
        self.cursor.execute("""SELECT stage FROM user_info WHERE user_id = {}""".format(user_id))
        result = (self.cursor.fetchall()[0])[-1]
        return result

    def update_stage(self, user_id, stage):
        self.cursor.execute(
            """UPDATE user_info SET stage = {} WHERE user_id = {}""".format("'"+stage+"'", user_id))

    def __del__(self):
            """Закрываем соединение с БД"""
            self.connection.close()
            self.cursor.close()
