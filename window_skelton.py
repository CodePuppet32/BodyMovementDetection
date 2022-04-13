import tkinter as tk
from tkinter import *
import classification_module
import cv2
import video_module
import webcam_module
import photo_module
from gloval_vars import *


class WindowSkeleton(tk.Tk):
    def __init__(self):
        classification_module.save_detection(cv2.imread('resources\\default_image.png'), 'resources\\')
        super().__init__()
        self.geometry('{}x{}'.format(600, 642))
        self.resizable(True, False)
        self.minsize(600, 642)
        self.title('Body Movement Detector')
        # top frame for the labels
        self.top_frame = Frame(self, background=background_color)
        Label(self.top_frame, text="CHOOSE FROM FOLLOWING", font=heading_text_font,
              fg='gray16', background=background_color, bd=2).pack(pady=10)
        self.top_frame.grid(row=0, column=0, sticky='nsew')

        # mid-frame to show video, photo or live webcam feed
        self.mid_frame = Frame(self, background='#7285DB', bd=4, highlightbackground='#49558C', highlightthickness=1)
        self.content_frame = Frame(self.mid_frame)

        # image frame to display images
        self.image_frame = Label(self.content_frame)

        # video frame to play videos
        self.frame_number = -1
        self.delay = 600
        self.video_frame = Frame(self.content_frame)

        # ------------- Frame navigation button Frame --------------
        frame_navigation_frame = Frame(self.video_frame)
        self.revert5 = Button(frame_navigation_frame, default_button, text='-{}'.format(backtrack_frames), state=DISABLED,
                              bg='#F2435F', activebackground='white', activeforeground='#F2435F', foreground='white',
                              command=lambda: video_module.show_frame(self, False, backtrack_frames))
        self.previous_detection = Button(frame_navigation_frame, default_button, text='Previous', state=DISABLED,
                                         bg='#F2435F',
                                         activebackground='white', activeforeground='#F2435F', foreground='white',
                                         command=lambda: video_module.show_frame(self, False))
        self.next_detection = Button(frame_navigation_frame, default_button, text='Next', bg='#F2435F',
                                     activebackground='white', activeforeground='#F2435F', foreground='white',
                                     command=lambda: video_module.show_frame(self, True))
        self.skip5 = Button(frame_navigation_frame, default_button, text='+{}'.format(skip_frames), bg='#F2435F',
                            activebackground='white', activeforeground='#F2435F', foreground='white',
                            command=lambda: video_module.show_frame(self, True, skip_frames))

        self.revert5.pack(side=LEFT)
        self.previous_detection.pack(side=LEFT, padx=(5, 0))
        self.next_detection.pack(side=LEFT, padx=5)
        self.skip5.pack(side=LEFT)
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

        # webcam frame to show webcam content
        self.webcam_frame = Label(self.content_frame)

        self.content_frame.place(relheight=1, relwidth=1)
        self.mid_frame.grid(row=1, column=0, sticky='nsew')

        # bottom frame for the buttons
        self.bottom_frame = Frame(self, background=background_color)
        # button container for the photo, video, webcam feed
        button_frame = Frame(self.bottom_frame, background='black')
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
        button_frame.place(relwidth=.8, relx=.1, rely=.2)
        # Close button
        Button(self.bottom_frame, default_button, text='Close', bg='#71B9BD', activeforeground='#71B9BD',
               command=lambda: video_module.stop_threads(self)).pack(side=BOTTOM, pady=8)
        self.bottom_frame.grid(row=2, column=0, sticky='nsew')

        # dynamic sizing of the three frames namely top, mid and bottom
        # self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=18)
        self.grid_rowconfigure(2, weight=2)
        self.grid_columnconfigure(0, weight=1)
