import os.path
import threading
import time
from tkinter import *
import numpy as np
from tkinter.ttk import Progressbar
import cv2
from PIL import ImageTk
from PIL import Image
import classification_module
from helper_functions import *
from tkinter import messagebox

fgModel = cv2.createBackgroundSubtractorMOG2()
photo_list = []
detection_set = set()


def keep_large_components(image, th):
    R = np.zeros(image.shape) < 0
    unique_labels = np.unique(image.flatten())
    for label in unique_labels:
        if label != 0:
            I2 = image == label
            if np.sum(I2) > th:
                R = R | I2
    return np.float32(255 * R)


def process_frame(frame, frame_save_path, fgmask_save_path):
    frame = cv2.resize(frame, dsize=(600, 400))
    # foreground mask
    fgmask = fgModel.apply(frame)
    k_r = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    fgmask = cv2.morphologyEx(np.float32(fgmask), cv2.MORPH_OPEN, k_r)
    _, label_image = cv2.connectedComponents(np.array(fgmask > 0, np.uint8))
    fgmask = keep_large_components(label_image, 800)
    cv2.imwrite(fgmask_save_path, fgmask)
    cv2.imwrite(frame_save_path, frame)


def save_frames(video_path, vid_name):
    vid_capture = cv2.VideoCapture(video_path)

    frame_directory = 'savedFrames\\frames\\' + vid_name
    fgmask_directory = 'savedFrames\\fgmask\\' + vid_name
    create_directory(frame_directory)
    create_directory(fgmask_directory)

    try:
        vid_frame_counter = 0
        ret, frame = vid_capture.read()
        while ret:
            frame_path = frame_directory + '\\' + str(vid_frame_counter) + '.jpg'
            fgmask_path = fgmask_directory + '\\' + str(vid_frame_counter) + '.jpg'
            threading.Thread(target=process_frame, args=(frame, frame_path, fgmask_path)).start()
            vid_frame_counter += 1
            # to read every 6th frame
            counter = 1
            while counter != 6:
                counter += 1
                vid_capture.read()
            ret, frame = vid_capture.read()
    finally:
        vid_capture.release()


def save_sequence(c, counter, output_path):
    global photo_list
    k = 1
    for frame in c:
        imName = str(counter) + '_' + str(k)
        finalPath = os.path.join(output_path, imName)
        classification_module.save_detection(frame, finalPath)
        photo_list.append(ImageTk.PhotoImage(Image.fromarray(frame[:, :, ::-1])))
        k += 1


def save_movement_frames(frame_directory, fgmask_directory, detection_directory, to_check):
    while to_check.is_alive():
        time.sleep(1)

    idx = []
    C = []

    for counter, img_name in enumerate(sorted(os.listdir(frame_directory), key=len)):
        fgmask = cv2.imread(os.path.join(fgmask_directory, img_name))

        if np.sum(fgmask) > 0:
            frame = cv2.imread(os.path.join(frame_directory, img_name))
            idx.append(counter)
            C.append(frame)

        if len(idx) >= 2 and idx[-1] > idx[-2] + 1:
            save_sequence(C, idx[0], detection_directory)
            idx = []
            C = []
    if len(C) >= 2:
        save_sequence(C, -1, detection_directory)


def show_video(self):
    global photo_list
    photo_list = []
    video_path = get_video_path()
    if video_path == '':
        messagebox.showerror('Empty Path', 'Path to video cannot be empty')
        return

    self.webcam_btn['state'] = DISABLED
    self.photo_btn['state'] = DISABLED
    self.video_btn['state'] = DISABLED

    vid_name = video_path.split('\\')[-1]
    frame_directory = 'savedFrames\\frames\\' + vid_name
    fgmask_directory = 'savedFrames\\fgmask\\' + vid_name
    detection_directory = 'detections\\videos\\' + vid_name
    create_directory(detection_directory)
    try:
        save_frame_thread = threading.Thread(target=save_frames, args=(video_path, vid_name))
        save_frame_thread.start()
        save_sequence_thread = threading.Thread(target=save_movement_frames, args=(
            frame_directory, fgmask_directory, detection_directory, save_frame_thread))
        save_sequence_thread.start()
        first_frame = threading.Thread(target=show_frame_thread, args=(self,))
        first_frame.start()
        progress_bar_thread = threading.Thread(target=progress_bar_thread_func, args=(first_frame,))
        progress_bar_thread.start()
        threading.Thread(target=enable_btn, args=(self, save_sequence_thread)).start()
    finally:
        return


def enable_btn(self, to_check):
    try:
        while to_check.is_alive():
            (time.sleep(2))
        self.webcam_btn['state'] = NORMAL
        self.photo_btn['state'] = NORMAL
        self.video_btn['state'] = NORMAL
    except RuntimeError:
        return


def show_frame_thread(self):
    global photo_list
    while len(photo_list) < 2:
        time.sleep(1)
    self.image_frame.place_forget()
    self.webcam_frame.place_forget()
    self.video_frame.place(x=0, y=0, relheight=1, relwidth=1)
    show_frame(self, True)


slideshowThread = None


def show_frame(self, is_next=True):
    global photo_list
    global slideshowThread

    # user clicked next or previous button while slideshow was being shown
    if slideshowThread is not None:
        frame_number = self.frame_number
        self.frame_number = len(photo_list)
        time.sleep(.9)
        self.frame_number = frame_number
        slideshowThread = None
        self.slideshow_label.pack_forget()
        self.video_label.pack()
        self.slideshow_btn.config(text='Slideshow')
        self.fast_btn['state'] = DISABLED
        self.slow_btn['state'] = DISABLED

    if is_next is True:
        self.frame_number += 1
        self.previous_detection['state'] = NORMAL
    else:
        self.frame_number -= 1
        self.next_detection['state'] = NORMAL
        self.slideshow_btn['state'] = NORMAL

    if self.frame_number == len(photo_list)-1:
        self.slideshow_btn['state'] = DISABLED
        self.next_detection['state'] = DISABLED
    if self.frame_number == 0:
        self.previous_detection['state'] = DISABLED

    self.video_label['image'] = photo_list[self.frame_number]
    self.video_label.image = photo_list[self.frame_number]


# Accepts one parameter - to_check->Thread
# shows progress bar until all the frames of the video are saved
# returns void
def progress_bar_thread_func(to_check):
    progress_bar_window = Toplevel()
    progress_bar_window.geometry('200x60')
    progress = Progressbar(progress_bar_window, orient=HORIZONTAL, length=100, mode='indeterminate')
    progress.pack()
    processing_text = Label(progress_bar_window, text='Processing Video ...')
    processing_text.pack()

    def progress_bar_update():
        processing_text_counter = 0
        while to_check.is_alive():
            progress['value'] = processing_text_counter % 100
            time.sleep(0.1)
            processing_text_counter += 2
        progress['value'] = 100
        processing_text['text'] = 'Almost Done'
        time.sleep(.2)

    progress_bar_update()
    progress_bar_window.destroy()


def slide_show(self):
    global slideshowThread
    global photo_list

    if slideshowThread is not None:
        frame_number = self.frame_number
        self.frame_number = len(photo_list)
        time.sleep(.9)
        slideshowThread = None
        self.frame_number = frame_number-1
        self.slideshow_label.pack_forget()
        self.video_label.pack(fill=Y)
        self.slideshow_btn.config(text='Slideshow')
        self.fast_btn['state'] = DISABLED
        self.slow_btn['state'] = DISABLED
        threading.Thread(target=show_frame, args=(self,)).start()
        return

    self.slideshow_btn.config(text='Pause')
    self.video_label.pack_forget()
    self.slideshow_label.pack()
    self.fast_btn['state'] = NORMAL
    self.slow_btn['state'] = NORMAL
    slideshowThread = threading.Thread(target=slideshow_thread, args=(self,))
    slideshowThread.start()


def slideshow_thread(self):
    global photo_list
    global slideshowThread
    num_photos = len(photo_list)
    self.previous_detection['state'] = NORMAL

    while self.frame_number < num_photos:
        self.slideshow_label['image'] = photo_list[self.frame_number]
        self.slideshow_label.image = photo_list[self.frame_number]
        cv2.waitKey(self.delay)
        self.frame_number += 1
        num_photos = len(photo_list)
    if self.frame_number == num_photos:
        self.fast_btn['state'] = DISABLED
        self.slow_btn['state'] = DISABLED
        self.next_detection['state'] = DISABLED
        self.slideshow_btn['state'] = DISABLED
        slideshowThread = None
        self.frame_number -= 2
        self.slideshow_label.pack_forget()
        self.video_label.pack(fill=Y)
        self.slideshow_btn.config(text='Slideshow')
        threading.Thread(target=show_frame, args=(self,)).start()


def faster(self):
    self.slow_btn['state'] = NORMAL
    if self.delay >= 200:
        self.delay -= 50
    else:
        self.fast_btn['state'] = DISABLED


def slower(self):
    self.fast_btn['state'] = NORMAL
    if self.delay <= 1000:
        self.delay += 50
    else:
        self.slow_btn['state'] = DISABLED
