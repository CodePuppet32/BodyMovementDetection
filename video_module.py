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
from gloval_vars import *

stop_slideshow = False
fgModel = cv2.createBackgroundSubtractorMOG2()
photo_list = []
detection_set = set()
current_read_frames = 0
num_saved_frames = 0
frame_directory = ''
fgmask_directory = ''
detection_directory = ''
save_frame_thread = threading.Thread
slideshowThread = None
counter = 0
stop_all_thread = False


# checked
def keep_large_components(image, th):
    global stop_all_thread
    if stop_all_thread:
        return
    R = np.zeros(image.shape) < 0
    unique_labels = np.unique(image.flatten())
    for label in unique_labels:
        if label != 0:
            I2 = image == label
            if np.sum(I2) > th:
                R = R | I2
    return np.float32(255 * R)


# checked
def process_frame(frame, frame_save_path, fgmask_save_path):
    global num_saved_frames
    global stop_all_thread
    if stop_all_thread:
        return
    frame = cv2.resize(frame, dsize=(600, 400))
    # foreground mask
    fgmask = fgModel.apply(frame)
    k_r = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    fgmask = cv2.morphologyEx(np.float32(fgmask), cv2.MORPH_OPEN, k_r)
    _, label_image = cv2.connectedComponents(np.array(fgmask > 0, np.uint8))
    fgmask = keep_large_components(label_image, 800)
    if stop_all_thread:
        return
    cv2.imwrite(fgmask_save_path, fgmask)
    if stop_all_thread:
        return
    cv2.imwrite(frame_save_path, frame)
    num_saved_frames += 1


def save_frames(video_path):
    vid_capture = cv2.VideoCapture(video_path)

    global frame_directory
    global fgmask_directory
    global stop_all_thread

    create_directory(frame_directory)
    create_directory(fgmask_directory)

    vid_frame_counter = 0
    ret, frame = vid_capture.read()
    while ret:
        if stop_all_thread:
            return
        frame_path = frame_directory + '\\' + str(vid_frame_counter) + '.jpg'
        fgmask_path = fgmask_directory + '\\' + str(vid_frame_counter) + '.jpg'
        threading.Thread(target=process_frame, args=(frame, frame_path, fgmask_path)).start()
        vid_frame_counter += 1
        # to read every 4th frame
        skip_counter = 1
        while skip_counter != read_nth_frame_video:
            skip_counter += 1
            vid_capture.read()
        ret, frame = vid_capture.read()
    vid_capture.release()


def save_frame_new():
    global save_frame_thread
    global num_saved_frames
    global stop_all_thread

    while save_frame_thread.is_alive():
        while num_saved_frames <= wait_for_n_frames and not stop_all_thread:
            time.sleep(.01)
        if stop_all_thread:
            return
        new_thread()
        num_saved_frames -= wait_for_n_frames


def new_thread():
    global counter
    global fgmask_directory
    global frame_directory
    global stop_all_thread
    idx = []
    C = []

    dir_list = sorted(os.listdir(frame_directory), key=len)

    for i in range(wait_for_n_frames):
        if stop_all_thread:
            return
        fgmask_dir = os.path.join(fgmask_directory, dir_list[i])
        frame_dir = os.path.join(frame_directory, dir_list[i])
        fgmask = cv2.imread(fgmask_dir)
        if np.sum(fgmask) > 0:
            frame = cv2.imread(frame_dir)
            idx.append(counter)
            C.append(frame)

        if len(idx) >= 2 and idx[-1] > idx[-2] + 1:
            save_sequence(C, idx[0], detection_directory)
            idx = []
            C = []

        counter += 1
        os.remove(fgmask_dir)
        os.remove(frame_dir)
    if len(idx) >= 2:
        save_sequence(C, len(idx), detection_directory)


def save_sequence(c, frame_counter, output_path):
    global photo_list
    global stop_all_thread
    k = 1
    try:
        for frame in c:
            if stop_all_thread:
                return
            imName = str(frame_counter) + '_' + str(k)
            finalPath = os.path.join(output_path, imName)
            classification_module.save_detection(frame, finalPath)
            photo_list.append(ImageTk.PhotoImage(Image.fromarray(frame[:, :, ::-1])))
            k += 1
    finally:
        return


# right now I am reading a video file
# extracting all its frames and saving image files in savedFrames
# What I want to do is
#       - Check if 20 or more frames have been saved
#               - Yes -> Read those 20 frames and save in a list
#                        Apply save_moment_frames function and save detections of those 20 frames and display
#               - No -> continue


# this is where thread will start its execution from checked
def show_video(self):
    global photo_list
    # to make sure we do not get frames of previous processed video
    # if we do not empty this list then we will get detected frames of previous video(s)
    photo_list = []

    # path to the video
    # it can be empty, so we need to check
    video_path = get_video_path()
    if video_path == '':
        messagebox.showerror('Empty Path', 'Path to video cannot be empty')
        return

    self.webcam_btn['state'] = DISABLED
    self.photo_btn['state'] = DISABLED
    self.video_btn['state'] = DISABLED

    vid_name = video_path.split('\\')[-1]
    global frame_directory
    global fgmask_directory
    global detection_directory
    global save_frame_thread

    frame_directory = 'savedFrames\\frames\\' + vid_name
    fgmask_directory = 'savedFrames\\fgmask\\' + vid_name
    detection_directory = 'detections\\videos\\' + vid_name
    create_directory(detection_directory)

    save_frame_thread = threading.Thread(target=save_frames, args=(video_path,))
    save_frame_thread.start()
    save_sequence_thread = threading.Thread(target=save_frame_new, args=())
    save_sequence_thread.start()
    first_frame = threading.Thread(target=show_frame_thread, args=(self,))
    first_frame.start()
    progress_bar_thread = threading.Thread(target=progress_bar_thread_func, args=(first_frame,))
    progress_bar_thread.start()
    threading.Thread(target=enable_btn, args=(self, save_sequence_thread)).start()


def enable_btn(self, to_check):
    global stop_all_thread
    try:
        while to_check.is_alive():
            if stop_all_thread:
                return
            (time.sleep(2))
        self.webcam_btn['state'] = NORMAL
        self.photo_btn['state'] = NORMAL
        self.video_btn['state'] = NORMAL
    except RuntimeError:
        return


def show_frame_thread(self):
    global stop_all_thread
    global photo_list
    while len(photo_list) < 5:
        if stop_all_thread:
            return
        time.sleep(1)
    self.image_frame.place_forget()
    self.webcam_frame.place_forget()
    self.video_frame.place(x=0, y=0, relheight=1, relwidth=1)
    show_frame(self, True)


def show_frame(self, is_next=True, num_frames=1):
    global photo_list
    global slideshowThread
    global stop_slideshow
    global stop_all_thread
    if stop_all_thread:
        return

    # user clicked next or previous button while slideshow was being shown
    if slideshowThread is not None:
        frame_number = self.frame_number
        stop_slideshow = True
        time.sleep(0.1)
        self.frame_number = frame_number
        slideshowThread = None
        self.slideshow_label.pack_forget()
        self.video_label.pack()
        self.slideshow_btn.config(text='Slideshow')
        self.fast_btn['state'] = DISABLED
        self.slow_btn['state'] = DISABLED

    if is_next is True:
        self.frame_number += num_frames
        self.previous_detection['state'] = NORMAL
        self.revert5['state'] = NORMAL
    else:
        self.frame_number -= num_frames
        self.next_detection['state'] = NORMAL
        self.skip5['state'] = NORMAL
        self.slideshow_btn['state'] = NORMAL

    if self.frame_number == len(photo_list) - 1:
        self.slideshow_btn['state'] = DISABLED
        self.next_detection['state'] = DISABLED
        self.skip5['state'] = DISABLED
    if self.frame_number == 0:
        self.previous_detection['state'] = DISABLED
        self.revert5['state'] = DISABLED
    if self.frame_number - backtrack_frames < 0:
        self.revert5['state'] = DISABLED
    if self.frame_number+skip_frames > len(photo_list)-1:
        self.skip5['state'] = DISABLED

    self.video_label['image'] = photo_list[self.frame_number]
    self.video_label.image = photo_list[self.frame_number]


# Accepts one parameter - to_check->Thread
# shows progress bar until all the frames of the video are saved
# returns void
def progress_bar_thread_func(to_check):
    global stop_all_thread
    if stop_all_thread:
        return
    progress_bar_window = Toplevel()
    progress_bar_window.geometry('200x60')
    progress = Progressbar(progress_bar_window, orient=HORIZONTAL, length=100, mode='indeterminate')
    progress.pack()
    processing_text = Label(progress_bar_window, text='Processing Video ...')
    processing_text.pack()

    try:
        def progress_bar_update():
            processing_text_counter = 0
            while to_check.is_alive():
                if stop_all_thread:
                    return
                progress['value'] = processing_text_counter % 100
                time.sleep(progress_bar_speed)
                processing_text_counter += 2
            progress['value'] = 100
            processing_text['text'] = 'Almost Done'
            time.sleep(.2)

        progress_bar_update()
        progress_bar_window.destroy()
    finally:
        return


def slide_show(self):
    global slideshowThread
    global photo_list
    global stop_slideshow
    global stop_all_thread

    if slideshowThread is not None:
        frame_number = self.frame_number
        stop_slideshow = True
        time.sleep(0.1)
        slideshowThread = None
        self.frame_number = frame_number - 1
        self.slideshow_label.pack_forget()
        self.video_label.pack(fill=Y)
        self.slideshow_btn.config(text='Slideshow')
        self.fast_btn['state'] = DISABLED
        self.slow_btn['state'] = DISABLED
        self.rabbit_btn['state'] = DISABLED
        self.turtle_btn['state'] = DISABLED
        if stop_all_thread:
            return
        threading.Thread(target=show_frame, args=(self,)).start()
        return

    self.slideshow_btn.config(text='Pause')
    self.video_label.pack_forget()
    self.slideshow_label.pack()
    self.fast_btn['state'] = NORMAL
    self.slow_btn['state'] = NORMAL
    self.rabbit_btn['state'] = NORMAL
    self.turtle_btn['state'] = NORMAL
    if stop_all_thread:
        return
    slideshowThread = threading.Thread(target=slideshow_thread, args=(self,))
    slideshowThread.start()


def slideshow_thread(self):
    global photo_list
    global slideshowThread
    global stop_slideshow
    num_photos = len(photo_list)
    self.previous_detection['state'] = NORMAL
    global stop_all_thread

    while self.frame_number < num_photos:
        if stop_all_thread:
            return
        self.slideshow_label['image'] = photo_list[self.frame_number]
        self.slideshow_label.image = photo_list[self.frame_number]
        if stop_slideshow:
            stop_slideshow = False
            return
        cv2.waitKey(self.delay)
        if stop_slideshow:
            stop_slideshow = False
            return
        self.frame_number += 1
        num_photos = len(photo_list)
    if self.frame_number == num_photos:
        self.fast_btn['state'] = DISABLED
        self.slow_btn['state'] = DISABLED
        self.rabbit_btn['state'] = DISABLED
        self.turtle['state'] = DISABLED
        self.next_detection['state'] = DISABLED
        self.slideshow_btn['state'] = DISABLED
        slideshowThread = None
        self.frame_number -= 2
        self.slideshow_label.pack_forget()
        self.video_label.pack(fill=Y)
        self.slideshow_btn.config(text='Slideshow')
        threading.Thread(target=btn_enable_thread, args=(self,)).start()
        threading.Thread(target=show_frame, args=(self,)).start()


def btn_enable_thread(self):
    global stop_all_thread
    global photo_list
    global save_frame_thread

    while save_frame_thread.is_alive():
        if stop_all_thread:
            return
        time.sleep(1)
        if self.frame_number < len(photo_list) - 1:
            self.next_detection['state'] = NORMAL
            self.slideshow_btn['state'] = NORMAL
            break

    if self.frame_number < len(photo_list) - 1:
        self.next_detection['state'] = NORMAL
        self.slideshow_btn['state'] = NORMAL


def faster(self):
    global stop_all_thread
    if stop_all_thread:
        return
    self.slow_btn['state'] = NORMAL
    self.turtle_btn['state'] = NORMAL
    if self.delay > lowest_slideshow_delay:
        self.delay -= 50
    else:
        self.fast_btn['state'] = DISABLED
        self.rabbit_btn['state'] = DISABLED


def slower(self):
    global stop_all_thread
    if stop_all_thread:
        return
    self.fast_btn['state'] = NORMAL
    self.rabbit_btn['state'] = NORMAL
    if self.delay < highest_slideshow_delay:
        self.delay += 50
    else:
        self.slow_btn['state'] = DISABLED
        self.turtle_btn['state'] = DISABLED


def slowest(self):
    global stop_all_thread
    if stop_all_thread:
        return
    self.fast_btn['state'] = NORMAL
    self.rabbit_btn['state'] = NORMAL
    self.delay = highest_slideshow_delay
    self.slow_btn['state'] = DISABLED
    self.turtle_btn['state'] = DISABLED


def fastest(self):
    global stop_all_thread
    if stop_all_thread:
        return
    self.slow_btn['state'] = NORMAL
    self.turtle_btn['state'] = NORMAL
    self.delay = lowest_slideshow_delay
    self.fast_btn['state'] = DISABLED
    self.rabbit_btn['state'] = DISABLED


def stop_threads(self):
    global stop_all_thread
    stop_all_thread = True
    self.destroy()
