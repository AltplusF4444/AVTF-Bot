import tkinter
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo
from bot import VK
import threading
import sqlite3


class M(tkinter.Tk):

    def __init__(self):
        super().__init__()

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

        self.btn_show_questions = ttk.Button(self, text="Show qe")
        self.btn_show_questions.pack()
        self.btn_show_questions['command'] = self.questions

        self.lbl_qe = ttk.Label(self)
        self.lbl_qe.pack()

    def questions(self):
        try:
            conn = sqlite3.connect(r"C:/Users/Maxim/DataGripProjects/DBAVTF/DBAVTF.sqlite")
            cursor = conn.cursor()
            cursor.execute("SELECT text FROM Questions;")
            results_text = cursor.fetchall()

        except (sqlite3.Error, sqlite3.Warning, sqlite3.OperationalError) as err:
            print("He удалось подключиться к БД")
            self.lbl_qe.configure(text='He удалось подключиться к БД')

        else:
            msg = ''
            n = 1
            for text in results_text:
                cursor.execute("SELECT id_user FROM Questions WHERE text = (?);", text)
                result_id = cursor.fetchone()
                msg += str(n) + ') ' + str(text[0]) + ' id: ' + str(result_id[0]) + '\n'
                n += 1
            self.lbl_qe.configure(text=msg)
            conn.close()

    def start_bot(self):
        self.Vk.thread_stop = False
        AVTF_Bot = threading.Thread(target=self.Vk.start)
        AVTF_Bot.start()
        self.lbl_main.configure(text='Бот включен')
        self.btn_start_bot.configure(state=DISABLED)
        self.btn_stop_bot.configure(state=ACTIVE)

    def stop_bot(self):
        self.Vk.thread_stop = True
        self.lbl_main.configure(text='Бот выключен')
        self.btn_start_bot.configure(state=ACTIVE)
        self.btn_stop_bot.configure(state=DISABLED)

    def start(self):
        self.mainloop()

    def stop(self):

        self.destroy()


if __name__ == '__main__':
    m = M()
    m.start()
