import tkinter as tk
from tkinter import *
from tkinter.ttk import Progressbar
import classification_module
import cv2
import video_module
import webcam_module
import default_parameter_module
import system_usage_module
from tkinter import colorchooser
# import detections_module
import photo_module
from gloval_vars import *
import os

class WindowSkeleton(tk.Tk):
    def __init__(self):
        file_path = os.path.realpath(__file__)
        file_path = os.path.dirname(file_path)
        resources_path = os.path.join(file_path, 'resources')
        classification_module.save_detection(60, cv2.imread(os.path.join(resources_path, 'default_image.png')),
                                             resources_path)
        super().__init__()
        self.geometry('{}x{}'.format(700, 800))
        self.resizable(True, True)
        self.minsize(700, 750)
        self.title('Body Movement Detector')

        # default parameters
        self.minimum_probability = 60
        self.read_nth_frame_video = 12
        self.detection_after_processing_n_frames = 50
        self.detection_speed = 'normal'
        self.num_detections_before_presented = 5
        self.default_slideshow_delay = 600
        self.highest_slideshow_delay = 900
        self.lowest_slideshow_delay = 300
        self.backtrack_frames = 10
        self.skip_frames = 10
        self.progress_bar_speed = 0.1
        self.background_color = '#E0A744'

        # top frame for the labels
        self.top_frame = Frame(self, background=self.background_color)
        self.select_color_btn = Button(self.top_frame, default_button, text="Select theme", width=12,
                                       background=self.background_color, command=lambda: choose_color(self))
        self.select_color_btn.place(y=14, relx=.5, anchor=CENTER)
        system_usage_module.show_usage(self)
        self.top_label = Label(self.top_frame, text="CHOOSE FROM FOLLOWING", font=heading_text_font,
                               fg='gray16', background=self.background_color, bd=2)
        self.top_label.place(relx=.5, rely=.6, anchor=CENTER)
        self.top_frame.grid(row=0, column=0, sticky='nsew')

        # mid-frame to show video, photo or live webcam feed
        self.mid_frame = Frame(self, background='#7285DB', bd=4, highlightbackground='#49558C', highlightthickness=1)
        self.content_frame = Frame(self.mid_frame)
        # image frame to display images
        # webcam frame to show webcam content
        self.webcam_frame = Label(self.content_frame)
        self.image_frame = Label(self.content_frame)
        self.video_frame = Frame(self.content_frame)
        self.frame_number = -1
        self.delay = 600
        # ------------- Frame navigation button Frame --------------
        frame_navigation_frame = Frame(self.video_frame)
        self.detection_over_total_bar = Progressbar(frame_navigation_frame)
        self.revert5 = Button(frame_navigation_frame, default_button, text='-{}'.format(self.backtrack_frames),
                              state=DISABLED,
                              bg='#F2435F', activebackground='white', activeforeground='#F2435F', foreground='white',
                              command=lambda: video_module.show_frame(self, False, self.backtrack_frames))
        self.previous_detection = Button(frame_navigation_frame, default_button, text='Previous', state=DISABLED,
                                         bg='#F2435F',
                                         activebackground='white', activeforeground='#F2435F', foreground='white',
                                         command=lambda: video_module.show_frame(self, False))
        self.pause_detection = Button(frame_navigation_frame, default_button, text='Pause', bg='#F2435F',
                                     activebackground='white', activeforeground='#F2435F', foreground='white',
                                     command=lambda: video_module.toggle_detection(self))
        self.next_detection = Button(frame_navigation_frame, default_button, text='Next', bg='#F2435F',
                                     activebackground='white', activeforeground='#F2435F', foreground='white',
                                     command=lambda: video_module.show_frame(self, True))
        self.skip5 = Button(frame_navigation_frame, default_button, text='+{}'.format(self.skip_frames), bg='#F2435F',
                            activebackground='white', activeforeground='#F2435F', foreground='white',
                            command=lambda: video_module.show_frame(self, True, self.skip_frames))
        self.num_frame_label = Label(frame_navigation_frame, font=button_font)

        self.detection_over_total_bar.pack(side=LEFT, padx=(0, 5))
        self.revert5.pack(side=LEFT)
        self.previous_detection.pack(side=LEFT, padx=(5, 0))
        self.pause_detection.pack(side=LEFT, padx=(5, 0))
        self.next_detection.pack(side=LEFT, padx=5)
        self.skip5.pack(side=LEFT)
        self.num_frame_label.pack(side=RIGHT)
        frame_navigation_frame.pack(side=BOTTOM)

        # ------------ slideshow button Frame -------------------
        slideshow_btn_frame = Frame(self.video_frame)
        self.turtle_btn = Button(slideshow_btn_frame, default_button, text='Turtle', bg='#4338A3', state=DISABLED,
                                 activebackground='white', activeforeground='#4338A3', foreground='white',
                                 command=lambda: video_module.slowest(self))
        self.slow_btn = Button(slideshow_btn_frame, default_button, text='Slower', bg='#4338A3', state=DISABLED,
                               activebackground='white', activeforeground='#4338A3', foreground='white',
                               command=lambda: video_module.slower(self))
        self.slideshow_btn = Button(slideshow_btn_frame, default_button, text='Slideshow', bg='#4338A3',
                                    activebackground='white', activeforeground='#4338A3', foreground='white',
                                    command=lambda: video_module.slide_show(self))
        self.fast_btn = Button(slideshow_btn_frame, default_button, text='Faster', bg='#4338A3', state=DISABLED,
                               activebackground='white', activeforeground='#4338A3', foreground='white',
                               command=lambda: video_module.faster(self))
        self.rabbit_btn = Button(slideshow_btn_frame, default_button, text='Rabbit', bg='#4338A3', state=DISABLED,
                                 activebackground='white', activeforeground='#4338A3', foreground='white',
                                 command=lambda: video_module.fastest(self))

        self.turtle_btn.pack(side=LEFT, padx=10)
        self.slow_btn.pack(side=LEFT)
        self.slideshow_btn.pack(side=LEFT, padx=10)
        self.fast_btn.pack(side=LEFT)
        self.rabbit_btn.pack(side=LEFT, padx=10)
        slideshow_btn_frame.pack(side=TOP)

        self.video_label = Label(self.video_frame)
        self.slideshow_label = Label(self.video_frame)
        self.video_label.pack(fill=Y)
        self.content_frame.place(relheight=1, relwidth=1)
        self.mid_frame.grid(row=1, column=0, sticky='nsew')

        # bottom frame for the buttons
        self.bottom_frame = Frame(self, background=self.background_color)
        # button container for the photo, video, webcam feed
        button_frame = Frame(self.bottom_frame)
        self.photo_btn = Button(button_frame, default_button, text='Image', bg='#3BCC59', activeforeground='#3BCC59',
                                command=lambda: photo_module.show_photo(self))
        self.photo_btn.grid(row=0, column=0, sticky='ew')
        self.video_btn = Button(button_frame, default_button, text='Video', bg='#FF71A5', activeforeground='#FF71A5',
                                command=lambda: video_module.show_video(self))
        self.video_btn.grid(row=0, column=1, sticky='ew')
        self.webcam_btn = Button(button_frame, default_button, text='WebCam', bg='#FFCC9E', activeforeground='#FFCC9E',
                                 command=lambda: webcam_module.show_webcam(self))
        self.webcam_btn.grid(row=0, column=2, sticky='ew')
        # allowing the buttons to resize dynamically
        for col in range(3):
            button_frame.grid_columnconfigure(col, weight=1)
        button_frame.pack(fill=BOTH, padx=20, pady=(20, 10))
        # Close button
        bottom_btn_frame = Frame(self.bottom_frame)
        self.close_btn = Button(bottom_btn_frame, default_button, text='Close', bg='#F75757',
                                activeforeground='#F75757',
                                command=lambda: video_module.stop_threads(self))
        self.see_detections_btn = Button(bottom_btn_frame, default_button, text='View Detections', bg='#26E3F7',
                                         activeforeground='#26E3F7')
        self.change_def_parameters = Button(bottom_btn_frame, default_button, text='Default Parameters',
                                            bg='#B18BD6', activeforeground='#B18BD6',
                                            command=lambda: default_parameter_module.set_default_vars(self))
        self.close_btn.grid(row=0, column=1, sticky='ew')
        self.see_detections_btn.grid(row=0, column=0, sticky='ew')
        self.change_def_parameters.grid(row=0, column=2, sticky='ew')
        bottom_btn_frame.pack(fill=BOTH, padx=20, pady=(10, 0))
        for col in range(3):
            bottom_btn_frame.grid_columnconfigure(col, weight=1)
        self.bottom_frame.grid(row=2, column=0, sticky='nsew')

        # dynamic sizing of the three frames namely top, mid and bottom
        # self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=18)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=3)
        self.grid_columnconfigure(0, weight=1)


def choose_color(self):
    color_code = colorchooser.askcolor(title='Choose color')
    self.top_frame['background'] = color_code[1]
    self.bottom_frame['background'] = color_code[1]
    self.top_label['background'] = color_code[1]
    self.mem_label['background'] = color_code[1]
    self.cpu_label['background'] = color_code[1]
    self.background_color = color_code[1]
    self.select_color_btn['background'] = color_code[1]