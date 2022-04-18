import threading
import time
import psutil
from tkinter.ttk import Progressbar
from tkinter import *


def show_usage(self):
    threading.Thread(target=show_system_usage, args=(self,)).start()
    system_usage_frame = Frame(self.top_frame)
    Label(system_usage_frame, text='CPU').grid(row=0, column=0)
    Label(system_usage_frame, text='MEM').grid(row=0, column=1)
    self.progress_bar_one = Progressbar(system_usage_frame, maximum=100, orient='vertical')
    self.progress_bar_two = Progressbar(system_usage_frame, maximum=100, orient='vertical')
    self.progress_bar_two.grid(row=1, column=1)
    self.progress_bar_one.grid(row=1, column=0)
    system_usage_frame.pack(side=LEFT)
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
