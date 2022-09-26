import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from settings import token
keyboard1 = VkKeyboard(one_time=False, inline=True)
keyboard1.add_button("Расписание событий факультета", color=VkKeyboardColor.POSITIVE)
keyboard1.add_openlink_button("Староста факультета", link="https://vk.com/altf4444")


def main():
    try:
        vk_session = vk_api.VkApi(token=token)

    except vk_api.AuthError as error_msg:
        print("Not auth", error_msg)
        return 1

    longpoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if event.text == 'Hi' or event.text == 'Привет':
                if event.from_user:
                    vk.messages.send(
                        user_id=event.user_id,
                        message='Привет',
                        keyboard=keyboard1.get_keyboard(),
                        random_id=get_random_id()
                    )
                elif event.from_chat:
                    vk.messages.send(
                        chat_id=event.chat_id,
                        message='Ваш текст',
                        random_id=get_random_id()
                    )
            elif event.text == 'Расписание событий факультета':
                if event.from_user:
                    vk.messages.send(
                        user_id=event.user_id,
                        message='Тут будет расписание',
                        keyboard=keyboard1.get_keyboard(),
                        random_id=get_random_id()
                    )
                elif event.from_chat:
                    vk.messages.send(
                        chat_id=event.chat_id,
                        message='Тут будет расписание',
                        random_id=get_random_id()
                    )
    return 0


if __name__ == '__main__':
    main()


