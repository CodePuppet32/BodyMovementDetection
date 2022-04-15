import threading
from tkinter import *
from tkinter.ttk import Progressbar
import time
import os
import shutil


def progress_bar_thread_func(to_check):
    global install_window
    progress = Progressbar(install_window, orient=HORIZONTAL, length=100, mode='indeterminate')
    progress.pack()
    processing_text = Label(install_window, text='Installing Necessary files')
    processing_text.pack()

    def progress_bar_update():
        processing_text_counter = 0
        while to_check.is_alive():
            progress['value'] = processing_text_counter % 100
            time.sleep(0.1)
            processing_text_counter += 2
    progress_bar_update()
    progress['value'] = 100
    processing_text['text'] = 'Installation successful.'
    close_btn['text'] = 'Run Program'
    close_btn['state'] = NORMAL


def install_modules():
    os.system('pip3 install --upgrade pip')
    os.system('pip install urllib3')
    import urllib3
    os.system('pip3 install -r requirements.txt')

    resnet_model_path = 'models\\resnet50_coco_best_v2.1.0.h5'
    if not os.path.exists(resnet_model_path):
        os.mkdir('models')
        url = 'https://github.com/fizyr/keras-retinanet/releases/download/0.5.1/resnet50_coco_best_v2.1.0.h5'
        c = urllib3.PoolManager()

        with c.request('GET', url, preload_content=False) as resp:
            with open(resnet_model_path, 'wb') as out_file:
                shutil.copyfileobj(resp, out_file)


install_window = Tk()
install_window.title('Setup in Progress')
install_window.geometry('200x80')
close_btn = Button(install_window, text='Please Wait', state=DISABLED, command=install_window.destroy)
close_btn.pack(side=BOTTOM, pady=8)
install_module_thread = threading.Thread(target=install_modules, args=())
install_module_thread.start()
progress_bar_thread = threading.Thread(target=progress_bar_thread_func, args=(install_module_thread,))
progress_bar_thread.start()
install_window.mainloop()
