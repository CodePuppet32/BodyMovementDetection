import os
from tkinter import *
from gloval_vars import *
import cv2
from PIL import ImageTk, Image

background = '#AAF9FF'
detection_folder_btn_frame = Frame()
close_btn = Button()
image_label = Label()


def get_num_detections_photos():
    detection_directory = 'detections\\photos\\'
    try:
        return len(os.listdir(detection_directory))
    except FileNotFoundError:
        return 0


def get_num_detections_videos():
    detection_directory = 'detections\\videos\\'
    try:
        return len(os.listdir(detection_directory))
    except FileNotFoundError:
        return 0


def get_num_detections_webcam():
    detection_directory = 'detections\\webcam\\'
    try:
        return len(os.listdir(detection_directory))
    except FileNotFoundError:
        return 0


def show_image(path):
    global image_label
    image = Image.open(path)
    image = ImageTk.PhotoImage(image)
    image_label['image'] = image
    image_label.image = image


def see_photos():
    global image_label
    detection_directory = 'detections\\photos\\'
    image_list = []
    for image in os.listdir(detection_directory):
        image_list.append(image)

    max_height = 600
    height = min(max(len(image_list) * 25, 200), max_height)

    parent = Tk()
    parent.geometry('960x{}'.format(height))
    canvas = Canvas(parent)
    scroll_y = Scrollbar(parent, orient='vertical', command=canvas.yview)

    image_list_frame = Frame(canvas, background='black')
    image_label = Label(parent)

    for image in image_list:
        Button(image_list_frame, list_button, text=image, command=lambda: show_image(os.path.join(detection_directory, image)))\
            .pack(fill=X, expand=True)

    canvas.create_window(0, 0, anchor='center', window=image_list_frame)
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox('all'),
                     yscrollcommand=scroll_y.set)

    canvas.pack(fill=Y, side=LEFT)
    image_label.pack(side=LEFT, pady=20, fill=BOTH, expand=True, padx=10)
    scroll_y.pack(fill=Y, side=RIGHT)


def see_videos():
    detection_directory = 'detections\\videos\\'
    global detection_folder_btn_frame
    global close_btn
    detection_folder_btn_frame.pack_forget()
    close_btn['text'] = 'back'
    close_btn['command'] = lambda: view_detections(1)


def see_webcam():
    detection_directory = 'detections\\webcam\\'
    global detection_folder_btn_frame
    global close_btn
    detection_folder_btn_frame.pack_forget()
    close_btn['text'] = 'back'
    close_btn['command'] = lambda: view_detections(1)


def view_detections(self):
    global view_detections_window
    global background
    global close_btn
    global detection_folder_btn_frame

    detection_folder_btn_frame = Frame(view_detections_window, background=background)

    image_detection_btn = Button(detection_folder_btn_frame, default_button, text='Photos', background='#70F7CE',
                                 activeforeground='#70F7CE', command=see_photos)
    num_detected_images_label = Label(detection_folder_btn_frame, font=default_text_font
                                      , text=get_num_detections_photos(), background=background)
    video_detection_btn = Button(detection_folder_btn_frame, default_button, text='Videos', background='#F7BA89',
                                 activeforeground='#F7BA89', command=see_photos)
    num_detected_videos_label = Label(detection_folder_btn_frame, font=default_text_font
                                      , text=get_num_detections_videos(), background=background)
    webcam_detection_btn = Button(detection_folder_btn_frame, default_button, text='Webcam', background='#AB98F7',
                                  activeforeground='#AB98F7', command=see_photos)
    num_detected_webcam_label = Label(detection_folder_btn_frame, font=default_text_font
                                      , text=get_num_detections_webcam(), background=background)

    video_detection_btn.grid(row=1, column=0, sticky='ew')
    image_detection_btn.grid(row=0, column=0, sticky='ew')
    webcam_detection_btn.grid(row=2, column=0, sticky='ew')
    num_detected_images_label.grid(row=0, column=1, sticky='ew')
    num_detected_videos_label.grid(row=1, column=1, sticky='ew', pady=20)
    num_detected_webcam_label.grid(row=2, column=1, sticky='ew')
    for col in [0, 1]:
        detection_folder_btn_frame.grid_columnconfigure(col, weight=1)

    detection_folder_btn_frame.pack(fill=X, pady=40, padx=40)

    close_btn = Button(view_detections_window, default_button, background='#FF822F', activeforeground='#FF822F'
                       , text='Close', command=view_detections_window.destroy)
    close_btn.place(relx=0.5, anchor=CENTER, rely=0.9)


view_detections_window = Toplevel()
view_detections_window.geometry('300x280')
view_detections_window.title('Detections')
view_detections_window.configure(background=background)
view_detections_window.resizable(False, False)
view_detections(1)
view_detections_window.mainloop()
