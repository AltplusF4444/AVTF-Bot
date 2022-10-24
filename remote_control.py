import tkinter
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo
from bot import VK
import threading
import sqlite3
from time import sleep


class M(tkinter.Tk):

    def __init__(self):
        super().__init__()

        self.entry = None
        self.combo_box = None
        self.lbl_out = None
        self.a_w = None

        self.Vk = VK()

        self.title('Remote Control AVTF Bot')
        self.geometry('600x600')

        self.lbl_main = ttk.Label(self, text='Бот выключен')
        self.lbl_main.pack()

        self.btn_start_bot = ttk.Button(self, text="Старт Бота")
        self.btn_start_bot.pack()
        self.btn_start_bot.configure(command=self.start_bot)

        self.btn_stop_bot = ttk.Button(self, text="Стоп Бота", state=DISABLED)
        self.btn_stop_bot.pack()
        self.btn_stop_bot['command'] = self.stop_bot

        self.btn_show_questions = ttk.Button(self, text="Показать неотвеченные вопросы")
        self.btn_show_questions.pack()
        self.btn_show_questions['command'] = self.questions

        self.lbl_qe = ttk.Label(self)
        self.lbl_qe.pack()

        self.btn_qe_window = ttk.Button(self, text='Ответить на вопрос', command=self.answer_window)

    def get_id_users(self):
        try:
            conn = sqlite3.connect(r"C:/Users/Maxim/DataGripProjects/DBAVTF/DBAVTF.sqlite")
            cursor = conn.cursor()
            cursor.execute("SELECT id_user FROM Questions where check_a = 0;")
            results = cursor.fetchall()

        except (sqlite3.Error, sqlite3.Warning, sqlite3.OperationalError) as err:
            print("He удалось подключиться к БД")
            self.lbl_qe.configure(text='He удалось подключиться к БД')

        else:
            if results is None:
                return 'Нет данных'
            return results

    def answer_window(self):
        self.a_w = tkinter.Toplevel(self)
        lbl_a_w = ttk.Label(self.a_w, text='Выберите пользователя для ответа')
        self.lbl_out = ttk.Label(self.a_w,text='')
        self.combo_box = ttk.Combobox(self.a_w, values=self.get_id_users())
        btn_choose = ttk.Button(self.a_w, text='Выбрать', command=self.choose_id)

        lbl_a_w.pack()
        self.combo_box.pack()
        btn_choose.pack()
        self.lbl_out.pack()

    def choose_id(self):
        try:
            conn = sqlite3.connect(r"C:/Users/Maxim/DataGripProjects/DBAVTF/DBAVTF.sqlite")
            cursor = conn.cursor()
            choose_id = (self.combo_box.get(),)
            cursor.execute("SELECT text FROM Questions WHERE id_user = ? and check_a = 0;", choose_id)
            result_text = cursor.fetchone()

        except (sqlite3.Error, sqlite3.Warning, sqlite3.OperationalError) as err:
            print("He удалось подключиться к БД")
            self.lbl_out.configure(text='He удалось подключиться к БД')

        else:
            self.lbl_out.configure(text=str(result_text[0]))
            self.entry = ttk.Entry(self.a_w)
            btn_send_a = ttk.Button(self.a_w, text='Отправить', command=self.send_a)
            self.entry.pack()
            btn_send_a.pack()
            conn.close()

    def send_a(self):
        try:
            conn = sqlite3.connect(r"C:/Users/Maxim/DataGripProjects/DBAVTF/DBAVTF.sqlite")
            cursor = conn.cursor()
            choose_id = (self.combo_box.get(),)
            cursor.execute("SELECT msg_id FROM Questions WHERE id_user = ? and check_a = 0;", choose_id)
            result = cursor.fetchone()

        except (sqlite3.Error, sqlite3.Warning, sqlite3.OperationalError) as err:
            print("Ошибка отправки сообщения")
            self.lbl_out.configure(text='Ошибка отправки сообщения')

        else:
            sql_upd = """Update Questions set check_a = 1 where id_user = ? and text =
             (SELECT text FROM Questions WHERE id_user = ? and check_a = 0);"""
            cursor.execute(sql_upd, (self.combo_box.get(), self.combo_box.get()))
            conn.commit()
            self.Vk.send(self.entry.get(), self.combo_box.get(), result)
            conn.close()
            self.a_w.destroy()

    def questions(self):
        try:
            conn = sqlite3.connect(r"C:/Users/Maxim/DataGripProjects/DBAVTF/DBAVTF.sqlite")
            cursor = conn.cursor()
            cursor.execute("SELECT text FROM Questions WHERE check_a = 0;")
            results_text = cursor.fetchall()

        except (sqlite3.Error, sqlite3.Warning, sqlite3.OperationalError) as err:
            print("He удалось подключиться к БД")
            self.lbl_qe.configure(text='He удалось подключиться к БД')

        else:
            msg = ''
            if not results_text:
                msg = "Нет неотвеченных вопросов"
            else:
                n = 1
                for text in results_text:
                    cursor.execute("SELECT id_user FROM Questions WHERE text = (?);", text)
                    result_id = cursor.fetchone()
                    cursor.execute("SELECT check_a FROM Questions WHERE text = (?);", text)
                    result_ch = cursor.fetchone()
                    ans = 'Не отвечено'
                    if result_ch[0] == 1:
                        ans = 'Отвечено'
                    msg += str(n) + ') ' + str(text[0]) + ' id: ' + str(result_id[0]) + ' , ' + ans + '\n'
                    n += 1
            self.lbl_qe.configure(text=msg)
            self.btn_show_questions.configure(text='Обновить')
            conn.close()

    def start_bot(self):
        self.Vk.thread_stop = False
        AVTF_Bot = threading.Thread(target=self.Vk.start)
        AVTF_Bot.start()
        self.btn_start_bot.configure(state=DISABLED)
        sleep(3)
        if not AVTF_Bot.is_alive():
            self.lbl_main.configure(text='Ошибка включения бота')
            self.btn_start_bot.configure(state=ACTIVE)
        else:
            self.lbl_main.configure(text='Бот включен')
            self.btn_start_bot.configure(state=DISABLED)
            self.btn_stop_bot.configure(state=ACTIVE)
            self.btn_qe_window.pack()

    def stop_bot(self):
        self.Vk.thread_stop = True
        self.lbl_main.configure(text='Бот выключен')
        self.btn_start_bot.configure(state=ACTIVE)
        self.btn_stop_bot.configure(state=DISABLED)
        self.btn_qe_window.destroy()

    def start(self):
        self.mainloop()

    def stop(self):

        self.destroy()

    def __del__(self):
        self.Vk.thread_stop = True


if __name__ == '__main__':
    m = M()
    m.start()
    del m
