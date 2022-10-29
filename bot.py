import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from settings import token
import sqlite3
import datetime


class VK:
    def __init__(self):
        self.vk_session = None
        self.thread_stop = True
        self.MainKey = VkKeyboard(one_time=False, inline=True)
        self.MainKey.add_button("Расписание событий факультета", color=VkKeyboardColor.POSITIVE)
        self.MainKey.add_button("Должностные лица факультета", color=VkKeyboardColor.PRIMARY)
        self.MainKey.add_button("Сообщение администратору", color=VkKeyboardColor.SECONDARY)
        self.MainKey.add_line()
        self.MainKey.add_button("Проект <<Мягкие лапки>>", color=VkKeyboardColor.NEGATIVE)

        self.TeamKey = VkKeyboard(one_time=False, inline=True)
        Links = self.get_team()
        self.TeamKey.add_openlink_button("Староста факультета", link=str(Links[0][0]))
        self.TeamKey.add_openlink_button("Заместитель №1", link=str(Links[1][0]))
        self.TeamKey.add_line()
        self.TeamKey.add_openlink_button("Заместитель №2", link=str(Links[2][0]))
        self.TeamKey.add_openlink_button("Художественный руководитель", link=str(Links[3][0]))
        self.TeamKey.add_line()
        self.TeamKey.add_openlink_button("Руководитель медиа отдела", link=str(Links[4][0]))

        self.dogs = 'Проект << Мягкие лапки >> направлен на материальную помощь приюту "Верность"\nПо ссылке ниже вы ' \
                    'можете увидеть местоположение контейнера для корма и ссылку на денежную помощь в фонд помощи ' \
                    'бездомным животным'

        self.DogsKey = VkKeyboard(inline=True)
        self.DogsKey.add_vkpay_button(hash='action=transfer-to-group&group_id=204477345')
        self.DogsKey.add_line()
        self.DogsKey.add_button('Назад')

    @staticmethod
    def get_timetable():
        try:
            conn = sqlite3.connect(r"DBAVTF.sqlite")
        except (sqlite3.Error, sqlite3.Warning) as err:
            print("He удалось подключиться к БД: " + err)
        cursor = conn.cursor()
        cursor.execute("SELECT Name FROM Events;")
        results_n = cursor.fetchall()

        msg = ""
        for res in results_n:
            cursor.execute("SELECT date_in FROM Events WHERE Name = (?);", res)
            results_in = cursor.fetchone()
            cursor.execute("SELECT date_out FROM Events WHERE Name = (?);", res)
            results_out = cursor.fetchone()
            msg += str(res[0]) + " С " + str(results_in[0]) + " до " + \
                   str(results_out).split("'")[
                       1] + "\n"
        conn.close()
        return msg

    @staticmethod
    def set_qe(text, id_user, msg_id):
        try:
            conn = sqlite3.connect(r"DBAVTF.sqlite")
        except (sqlite3.Error, sqlite3.Warning) as err:
            print("He удалось подключиться к БД: " + err)
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO Questions(text, id_user, msg_id) 
           VALUES(?,?,?);""", (text, id_user, msg_id))
        conn.commit()
        conn.close()

    @staticmethod
    def set_log(log):
        try:
            conn = sqlite3.connect(r"DBAVTF.sqlite")
        except (sqlite3.Error, sqlite3.Warning) as err:
            print("He удалось подключиться к БД: " + err)
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO logs(log, datetime) 
           VALUES(?,?);""", (log, datetime.datetime.now()))
        conn.commit()
        conn.close()

    @staticmethod
    def get_team():
        try:
            conn = sqlite3.connect(r"DBAVTF.sqlite")
        except (sqlite3.Error, sqlite3.Warning) as err:
            print("He удалось подключиться к БД: " + err)
        cursor = conn.cursor()
        cursor.execute("SELECT Link FROM Team;")
        results = cursor.fetchall()
        conn.close()
        return results

    def start(self):
        try:
            self.vk_session = vk_api.VkApi(token=token)

        except vk_api.AuthError as error_msg:
            print("Not auth", error_msg)
            return 1

        LongPoll = VkLongPoll(self.vk_session)
        vk = self.vk_session.get_api()
        users = []

        for event in LongPoll.listen():
            if not self.thread_stop:
                if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                    if event.from_user:
                        if event.text == 'Привет' or event.text == 'Начать' or event.text == 'Назад':

                            vk.messages.send(
                                user_id=event.user_id,
                                message='Привет!',
                                keyboard=None,
                                random_id=get_random_id()
                            )
                            vk.messages.send(
                                user_id=event.user_id,
                                message='Вот что я умею:',
                                keyboard=self.MainKey.get_keyboard(),
                                random_id=get_random_id()
                            )

                            try:
                                users.pop(users.index(event.user_id))
                            except BaseException as BE:
                                self.set_log(str(BE))
                        elif event.text == 'Расписание событий факультета':

                            vk.messages.send(
                                user_id=event.user_id,
                                message='Вот что у нас запланировано:\n' + self.get_timetable(),
                                keyboard=self.MainKey.get_keyboard(),
                                random_id=get_random_id()
                            )
                            try:
                                users.pop(users.index(event.user_id))
                            except BaseException as BE:
                                self.set_log(str(BE))
                        elif event.text == 'Должностные лица факультета':

                            vk.messages.send(
                                user_id=event.user_id,
                                message='Должностные лица:\n',
                                keyboard=self.TeamKey.get_keyboard(),
                                random_id=get_random_id()
                            )
                            vk.messages.send(
                                user_id=event.user_id,
                                message='Вот что я умею:',
                                keyboard=self.MainKey.get_keyboard(),
                                random_id=get_random_id()
                            )
                            try:
                                users.pop(users.index(event.user_id))
                            except BaseException as BE:
                                self.set_log(str(BE))
                        elif event.text == 'Сообщение администратору':
                            vk.messages.send(
                                user_id=event.user_id,
                                message='Введите ваше сообщение',
                                random_id=get_random_id()
                            )
                            try:
                                users.index(event.user_id)
                            except BaseException as BE:
                                self.set_log(str(BE))
                                users.append(event.user_id)
                        elif event.text == 'Проект «Мягкие лапки»':
                            vk.messages.send(
                                user_id=event.user_id,
                                message=self.dogs,
                                lat='54.98707',
                                long='82.91492',
                                keyboard=self.DogsKey.get_keyboard(),
                                random_id=get_random_id()
                            )

                        elif event.user_id in users:
                            vk.messages.send(
                                user_id=event.user_id,
                                message='Ваше сообщение отправлено! Ждем ответа...',
                                keyboard=self.MainKey.get_keyboard(),
                                random_id=get_random_id()
                            )
                            users.pop(users.index(event.user_id))

                            self.set_qe(event.text, event.user_id, event.message_id)
                    elif event.from_chat:
                        if event.text == 'Привет':
                            vk.messages.send(
                                user_id=event.user_id,
                                message='Привет! Вот что я умею:',
                                keyboard=self.MainKey.get_keyboard(),
                                random_id=get_random_id()
                            )
            else:
                break
        return 0

    def send(self, msg, user_id, msg_id):
        try:
            self.vk_session = vk_api.VkApi(token=token)

        except vk_api.AuthError as error_msg:
            print("Not auth", error_msg)
            return 1
        else:
            vk = self.vk_session.get_api()
            vk.messages.send(
                user_id=user_id,
                message=msg,
                reply_to=msg_id,
                random_id=get_random_id()
            )
            vk.messages.send(
                user_id=user_id,
                message='Надеемся модератор смог ответить на ваш вопрос',
                keyboard=self.MainKey.get_keyboard(),
                random_id=get_random_id()
            )


if __name__ == '__main__':
    VKontacte = VK()
    VKontacte.start(0)
