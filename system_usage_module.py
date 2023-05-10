import threading
import time
import psutil
from tkinter.ttk import Progressbar
from tkinter import *
from gloval_vars import heading_text_font


def show_usage(self):
    threading.Thread(target=show_system_usage, args=(self,)).start()
    self.mem_label = Label(self.top_frame, font=heading_text_font, text='MEMORY', background=self.background_color)
    self.mem_label.place(relx=.05, rely=0.4)
    self.cpu_label = Label(self.top_frame, font=heading_text_font, text='CPU', background=self.background_color)
    self.cpu_label.place(relx=.95, rely=0.4, anchor=NE)
    self.progress_bar_one = Progressbar(self.top_frame, maximum=100, orient='horizontal')
    self.progress_bar_two = Progressbar(self.top_frame, maximum=100, orient='horizontal')
    self.progress_bar_two.place(relx=.05, y=10)
    self.progress_bar_one.place(relx=.95, y=10, anchor=NE)
    threading.Thread(target=show_system_usage, args=(self,)).start()


def show_system_usage(self):
    while self.winfo_exists():
        try:
            cpu_percent = psutil.cpu_percent(1)
            memory_percent = psutil.virtual_memory()[2]
            self.progress_bar_one['value'] = cpu_percent
            self.progress_bar_two['value'] = memory_percent
            time.sleep(0.1)
        except RuntimeError:
            return
