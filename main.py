import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from settings import token
import sqlite3
import datetime


def get_timetable():
    try:
        conn = sqlite3.connect(r"C:/Users/Maxim/DataGripProjects/DBAVTF/DBAVTF.sqlite")
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
        msg += str(res).split("'")[1] + " С " + str(results_in).split("'")[1] + " до " + str(results_out).split("'")[
            1] + "\n"
    conn.close()
    return msg


def set_qe(text, id_user):
    try:
        conn = sqlite3.connect(r"C:/Users/Maxim/DataGripProjects/DBAVTF/DBAVTF.sqlite")
    except (sqlite3.Error, sqlite3.Warning) as err:
        print("He удалось подключиться к БД: " + err)
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO Questions(text, id_user) 
       VALUES(?,?);""", (text, id_user))
    conn.commit()
    conn.close()


def set_log(log):
    try:
        conn = sqlite3.connect(r"C:/Users/Maxim/DataGripProjects/DBAVTF/DBAVTF.sqlite")
    except (sqlite3.Error, sqlite3.Warning) as err:
        print("He удалось подключиться к БД: " + err)
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO logs(log, datetime) 
       VALUES(?,?);""", (log, datetime.datetime.now()))
    conn.commit()
    conn.close()


def get_team():
    try:
        conn = sqlite3.connect(r"C:/Users/Maxim/DataGripProjects/DBAVTF/DBAVTF.sqlite")
    except (sqlite3.Error, sqlite3.Warning) as err:
        print("He удалось подключиться к БД: " + err)
    cursor = conn.cursor()
    cursor.execute("SELECT Link FROM Team;")
    results = cursor.fetchall()
    conn.close()
    return results


MainKey = VkKeyboard(one_time=False, inline=True)
MainKey.add_button("Расписание событий факультета", color=VkKeyboardColor.POSITIVE)
MainKey.add_button("Должностные лица факультета", color=VkKeyboardColor.PRIMARY)
MainKey.add_button("Сообщение администратору", color=VkKeyboardColor.SECONDARY)
MainKey.add_line()
MainKey.add_button("Проект <<Мягкие лапки>>", color=VkKeyboardColor.NEGATIVE)

TeamKey = VkKeyboard(one_time=False, inline=True)
Links = get_team()
TeamKey.add_openlink_button("Староста факультета", link=str(Links[0]).split("'")[1])
TeamKey.add_openlink_button("Заместитель №1", link=str(Links[1]).split("'")[1])
TeamKey.add_line()
TeamKey.add_openlink_button("Заместитель №2", link=str(Links[2]).split("'")[1])
TeamKey.add_openlink_button("Художественный руководитель", link=str(Links[3]).split("'")[1])
TeamKey.add_line()
TeamKey.add_openlink_button("Руководитель медиа отдела", link=str(Links[4]).split("'")[1])

dogs = 'Проект << Мягкие лапки >> направлен на материальную помощь приюту "Верность"\nПо ссылке ниже вы можете ' \
       'увидеть местоположение контейнера для корма и ссылку на денежную помощь в фонд помощи бездомным животным'


DogsKey = VkKeyboard(inline=True)
DogsKey.add_vkpay_button(hash='action=transfer-to-group&group_id=204477345')
DogsKey.add_button('Назад')


def main():
    try:
        vk_session = vk_api.VkApi(token=token)

    except vk_api.AuthError as error_msg:
        print("Not auth", error_msg)
        return 1

    LongPoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()
    users = []
    for event in LongPoll.listen():
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
                        keyboard=MainKey.get_keyboard(),
                        random_id=get_random_id()
                    )

                    try:
                        users.pop(users.index(event.user_id))
                    except BaseException as BE:
                        set_log(str(BE))
                elif event.text == 'Расписание событий факультета':

                    vk.messages.send(
                        user_id=event.user_id,
                        message='Вот что у нас запланировано:\n' + get_timetable(),
                        keyboard=MainKey.get_keyboard(),
                        random_id=get_random_id()
                    )
                    try:
                        users.pop(users.index(event.user_id))
                    except BaseException as BE:
                        set_log(str(BE))
                elif event.text == 'Должностные лица факультета':

                    vk.messages.send(
                        user_id=event.user_id,
                        message='Должностные лица:\n',
                        keyboard=TeamKey.get_keyboard(),
                        random_id=get_random_id()
                    )
                    vk.messages.send(
                        user_id=event.user_id,
                        message='Вот что я умею:',
                        keyboard=MainKey.get_keyboard(),
                        random_id=get_random_id()
                    )
                    try:
                        users.pop(users.index(event.user_id))
                    except BaseException as BE:
                        set_log(str(BE))
                elif event.text == 'Сообщение администратору':
                    vk.messages.send(
                        user_id=event.user_id,
                        message='Введите ваше сообщение',
                        random_id=get_random_id()
                    )
                    try:
                        users.index(event.user_id)
                    except BaseException as BE:
                        set_log(str(BE))
                        users.append(event.user_id)
                elif event.text == 'Проект «Мягкие лапки»':
                    vk.messages.send(
                        user_id=event.user_id,
                        message=dogs,
                        lat='54.98707',
                        long='82.91492',
                        keyboard=DogsKey.get_keyboard(),
                        random_id=get_random_id()
                    )

                elif event.user_id in users:
                    vk.messages.send(
                        user_id=event.user_id,
                        message='Ваше сообщение отправлено! Ждем ответа...',
                        keyboard=MainKey.get_keyboard(),
                        random_id=get_random_id()
                    )
                    users.pop(users.index(event.user_id))

                    set_qe(event.text, event.user_id)
            elif event.from_chat:
                if event.text == 'Привет':
                    vk.messages.send(
                        user_id=event.user_id,
                        message='Привет! Вот что я умею:',
                        keyboard=MainKey.get_keyboard(),
                        random_id=get_random_id()
                    )
    return 0


if __name__ == '__main__':
    main()
