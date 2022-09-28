import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from settings import token
import sqlite3


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
        msg += str(res).split("'")[1] + " С " + str(results_in).split("'")[1] + " до " + str(results_out).split("'")[1] + "\n"
    conn.close()
    return msg


def get_team():
    try:
        conn = sqlite3.connect(r"C:/Users/Maxim/DataGripProjects/DBAVTF/DBAVTF.sqlite")
    except (sqlite3.Error, sqlite3.Warning) as err:
        print("He удалось подключиться к БД: " + err)
    cursor = conn.cursor()
    cursor.execute("SELECT Link FROM Team;")
    results = cursor.fetchall()
    return results


MainKey = VkKeyboard(one_time=False, inline=True)
MainKey.add_button("Расписание событий факультета", color=VkKeyboardColor.POSITIVE)
MainKey.add_button("Должностные лица факультета", color=VkKeyboardColor.PRIMARY)



TeamKey = VkKeyboard(one_time=False, inline=True)
Links = get_team()
TeamKey.add_openlink_button("Староста факультета", link=str(Links[0]).split("'")[1])
TeamKey.add_openlink_button("Заместитель №1", link=str(Links[1]).split("'")[1])
TeamKey.add_line()
TeamKey.add_openlink_button("Заместитель №2", link=str(Links[2]).split("'")[1])
TeamKey.add_openlink_button("Художественный руководитель", link=str(Links[3]).split("'")[1])
TeamKey.add_line()
TeamKey.add_openlink_button("Руководитель медиа отдела", link=str(Links[4]).split("'")[1])


def main():

    try:
        vk_session = vk_api.VkApi(token=token)

    except vk_api.AuthError as error_msg:
        print("Not auth", error_msg)
        return 1

    LongPoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()

    for event in LongPoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if event.from_user:
                if event.text == 'Привет':

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
                elif event.text == 'Расписание событий факультета':
                    if event.from_user:
                        vk.messages.send(
                            user_id=event.user_id,
                            message='Вот что у нас запланировано:\n' + get_timetable(),
                            keyboard=MainKey.get_keyboard(),
                            random_id=get_random_id()
                        )
                elif event.text == 'Должностные лица факультета':
                    if event.from_user:
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


