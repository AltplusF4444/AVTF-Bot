import tkinter
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo
from bot import VK
import threading


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
