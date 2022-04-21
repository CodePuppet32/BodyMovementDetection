import threading
import time
from tkinter import *
from tkinter.ttk import Progressbar
from gloval_vars import *

to_check = True


def stop_progress_bar():
    global to_check
    to_check = False


def set_default_vars(self):
    global to_check
    to_check = True
    background = '#224275'
    set_default_vars_window = Toplevel()
    # set_default_vars_window.geometry('500x600')
    set_default_vars_window.title('Set default parameters')
    set_default_vars_window.configure(background=background)
    content_frame = Frame(set_default_vars_window, background=background)

    def_parameter_list = ['Jump N Frames', 'Detection Speed', 'Backtrack N Frames', 'Read nth Frame',
                          'Min Slideshow Delay', 'Max Slideshow Delay', 'Def Slideshow Delay',
                          'Show After', 'Detection After N', 'Minimum Probability', 'Progress Bar Speed']

    # color_list = ['#26E3F7', '#8544F7', '#F75757', '#F71FB1', '#0CF710', '#26E3F7', '#F75757', '#F71FB1']

    parameter_value_vars = [IntVar() for i in range(10)]
    parameter_value_vars.append(StringVar())
    parameter_value_vars[0].set(self.skip_frames)
    parameter_value_vars[1].set(5)
    parameter_value_vars[2].set(self.backtrack_frames)
    parameter_value_vars[3].set(self.read_nth_frame_video)
    parameter_value_vars[4].set(self.lowest_slideshow_delay)
    parameter_value_vars[5].set(self.highest_slideshow_delay)
    parameter_value_vars[6].set(self.default_slideshow_delay)
    parameter_value_vars[7].set(self.num_detections_before_presented)
    parameter_value_vars[8].set(self.detection_after_processing_n_frames)
    parameter_value_vars[9].set(self.minimum_probability)
    parameter_value_vars[10].set(self.progress_bar_speed)

    for i, parameter in enumerate(def_parameter_list):
        Label(content_frame, text=parameter.upper(), font=default_text_font_bold, foreground='white',
              background=background).grid(row=i, column=0, ipady=10, ipadx=10, sticky='ew')
        Entry(content_frame, textvariable=parameter_value_vars[i], font=button_font, width=5, borderwidth=1,
              background='white', relief='raised', foreground='#224275').grid(row=i, column=1)

    progress_bar = Progressbar(set_default_vars_window, orient=HORIZONTAL, length=100, mode='indeterminate')
    progress_bar.pack(pady=(10,))
    threading.Thread(target=play_progress_bar, args=(self, progress_bar)).start()
    content_frame.grid_columnconfigure(0, weight=1)
    content_frame.pack(padx=10, pady=10)

    button_frame = Frame(content_frame, background=background)
    Button(button_frame, default_button, text='Save', fg='white', activebackground='white',
           command=lambda: apply(self, parameter_value_vars)).pack(side=LEFT, padx=(0, 5))
    Button(button_frame, default_button, text='Close', fg='white', activebackground='white',
           command=lambda: (stop_progress_bar(), set_default_vars_window.destroy())).pack(side=LEFT, padx=(5, 0))
    button_frame.grid(row=len(parameter_value_vars), column=0, columnspan=2, ipady=10)


def play_progress_bar(self, progress_bar):
    global to_check
    counter = 0
    while to_check:
        progress_bar['value'] = counter % 100
        time.sleep(self.progress_bar_speed)
        counter += 2


def apply(self, parameter_value_vars):
    detection_speed_list = ['normal', 'fast', 'faster', 'fastest', 'flash']
    self.skip_frames = parameter_value_vars[0].get()
    self.detection_speed = detection_speed_list[parameter_value_vars[1].get() - 1]
    self.backtrack_frames = parameter_value_vars[2].get()
    self.read_nth_frame_video = parameter_value_vars[3].get()
    self.lowest_slideshow_delay = parameter_value_vars[4].get()
    self.highest_slideshow_delay = parameter_value_vars[5].get()
    self.default_slideshow_delay = parameter_value_vars[6].get()
    self.num_detections_before_presented = parameter_value_vars[7].get()
    self.detection_after_processing_n_frames = parameter_value_vars[8].get()
    self.minimum_probability = parameter_value_vars[9].get()
    self.progress_bar_speed = float(parameter_value_vars[10].get())
    self.skip5['text'] = '+{}'.format(self.skip_frames)
    self.revert5['text'] = '-{}'.format(self.backtrack_frames)
