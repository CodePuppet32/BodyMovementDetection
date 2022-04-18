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

stop_slideshow = False
fgModel = cv2.createBackgroundSubtractorMOG2()
photo_list = []
detection_set = set()
current_read_frames = 0
num_saved_frames = 0
detected_frames = 0
vid_frame_counter = 0
frame_directory = ''
fgmask_directory = ''
detection_directory = ''
save_frame_thread = threading.Thread
save_sequence_thread = threading.Thread
slideshowThread = None
stop_all_thread = False
counter = 0


def show_detections_over_total_frames(self):
    global vid_frame_counter
    global detected_frames
    try:
        while 1:
            self.detection_over_total_bar['maximum'] = vid_frame_counter
            self.detection_over_total_bar['value'] = detected_frames
            time.sleep(0.1)
    except RuntimeError:
        return


# this is where thread will start its execution from checked
def show_video(self):
    global photo_list
    global frame_directory
    global fgmask_directory
    global detection_directory
    global save_sequence_thread
    global save_frame_thread
    global detected_frames
    global vid_frame_counter
    detected_frames = 0
    vid_frame_counter = 0

    # to make sure we do not get frames of previous processed video
    # if we do not empty this list then we will get detected frames of previous video(s)
    photo_list = []
    self.frame_number = -1

    # path to the video
    # it can be empty, so we need to check
    video_path = get_video_path()
    if video_path == '':
        messagebox.showerror('Empty Path', 'Path to video cannot be empty')
        return

    vid_name = video_path.split('\\')[-1]
    frame_directory = 'savedFrames\\frames\\' + vid_name
    fgmask_directory = 'savedFrames\\fgmask\\' + vid_name
    detection_directory = 'detections\\videos\\' + vid_name
    create_directory(detection_directory)

    # disable buttons to make sure memory leak problem is prevented
    self.webcam_btn['state'] = DISABLED
    self.photo_btn['state'] = DISABLED
    self.video_btn['state'] = DISABLED
    self.close_btn['state'] = DISABLED

    # thread to extract and process frames of video
    save_frame_thread = threading.Thread(target=save_frames, args=(self, video_path))
    save_frame_thread.start()
    # thread to send processed frames to the ImageAI for detection
    save_sequence_thread = threading.Thread(target=detect_and_save_frames_helper, args=(self,))
    save_sequence_thread.start()
    # thread to show the detected frames
    first_frame = threading.Thread(target=show_frame_thread, args=(self,))
    first_frame.start()
    # progress bar thread
    progress_bar_thread = threading.Thread(target=progress_bar_thread_func, args=(first_frame, self))
    progress_bar_thread.start()
    threading.Thread(target=show_detections_over_total_frames, args=(self,)).start()


# this functions reads video file frame after frame and starts a new thread (process_frame) for processing
def save_frames(self, video_path):
    vid_capture = cv2.VideoCapture(video_path)
    flag = True
    global frame_directory
    global fgmask_directory
    global stop_all_thread
    global vid_frame_counter

    create_directory(frame_directory)
    create_directory(fgmask_directory)

    vid_frame_counter = 0
    ret, frame = vid_capture.read()
    while ret:
        if stop_all_thread:
            return
        if flag and num_saved_frames > self.detection_after_processing_n_frames:
            # to let detection_thread take over CPU for its setup
            time.sleep(5)
            flag = False
        frame_path = frame_directory + '\\' + str(vid_frame_counter) + '.jpg'
        fgmask_path = fgmask_directory + '\\' + str(vid_frame_counter) + '.jpg'
        threading.Thread(target=process_frame, args=(frame, frame_path, fgmask_path)).start()
        vid_frame_counter += 1
        # to read every 4th frame
        skip_counter = 1
        while skip_counter != self.read_nth_frame_video:
            skip_counter += 1
            vid_capture.read()
        ret, frame = vid_capture.read()

    self.webcam_btn['state'] = NORMAL
    self.photo_btn['state'] = NORMAL
    self.video_btn['state'] = NORMAL
    vid_capture.release()


# this functions takes in a frame, processes the frame and saved the frame and masked image in local storage
def process_frame(frame, frame_save_path, fgmask_save_path):
    try:
        global num_saved_frames
        frame = cv2.resize(frame, dsize=(600, 400))
        # foreground mask
        fgmask = fgModel.apply(frame)
        k_r = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        fgmask = cv2.morphologyEx(np.float32(fgmask), cv2.MORPH_OPEN, k_r)
        _, label_image = cv2.connectedComponents(np.array(fgmask > 0, np.uint8))
        fgmask = keep_large_components(label_image, 800)
        cv2.imwrite(fgmask_save_path, fgmask)
        cv2.imwrite(frame_save_path, frame)
        num_saved_frames += 1
    except AttributeError or cv2.error:
        return


# this functions removes noise from the masked image
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


# This function check whether enough frames have been processed, masked and saved in local storage
# If specified number of frames have been saved it will call
def detect_and_save_frames_helper(self):
    global save_frame_thread
    global num_saved_frames
    global stop_all_thread

    while save_frame_thread.is_alive():
        if num_saved_frames <= self.detection_after_processing_n_frames and not stop_all_thread:
            if stop_all_thread:
                return
            time.sleep(.1)
        else:
            detect_and_save_n_frames(self)
            num_saved_frames -= self.detection_after_processing_n_frames

    while num_saved_frames > self.detection_after_processing_n_frames:
        detect_and_save_n_frames(self)
        num_saved_frames -= self.detection_after_processing_n_frames

    detect_and_save_n_frames(self)


# this function detects movement in specified number of frames
def detect_and_save_n_frames(self):
    global counter
    global fgmask_directory
    global frame_directory
    global stop_all_thread
    global detected_frames
    idx = []
    C = []

    dir_list = sorted(os.listdir(frame_directory), key=len)

    for i in range(min(len(dir_list), self.detection_after_processing_n_frames)):
        detected_frames += 1
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


# this functions detects the objects in frame where movement was observed and saves in local storage
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


# this threads waits for specified number of detections made and calls function that is responsible for showing frames
# on screen
def show_frame_thread(self):
    global stop_all_thread
    global photo_list
    while len(photo_list) < self.num_detections_before_presented:
        if stop_all_thread:
            return
        time.sleep(1)
    try:
        self.image_frame.place_forget()
        self.webcam_frame.place_forget()
    except AttributeError:
        pass
    self.video_frame.place(x=0, y=0, relheight=1, relwidth=1)
    show_frame(self, True)


# this functions shows the output on the screen
# is_next = True means user wants to see the next detection
# num_frames is the nth frame from current frame to be shown
def show_frame(self, is_next=True, num_frames=1):
    global photo_list
    global slideshowThread
    global stop_slideshow
    global stop_all_thread
    if stop_all_thread:
        return
    try:
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
            self.turtle_btn['state'] = DISABLED
            self.slow_btn['state'] = DISABLED
            self.rabbit_btn['state'] = DISABLED

        if is_next is True:
            self.frame_number += num_frames
            self.previous_detection['state'] = NORMAL
            self.revert5['state'] = NORMAL
        else:
            self.frame_number -= num_frames
            self.next_detection['state'] = NORMAL
            self.skip5['state'] = NORMAL
            self.slideshow_btn['state'] = NORMAL

        if (len(photo_list)-self.skip_frames) < self.frame_number:
            self.skip5['state'] = DISABLED
        if self.frame_number == len(photo_list) - 1:
            self.slideshow_btn['state'] = DISABLED
            self.next_detection['state'] = DISABLED
        if self.frame_number - self.backtrack_frames < 0:
            self.revert5['state'] = DISABLED
        if self.frame_number == 0:
            self.previous_detection['state'] = DISABLED

        self.video_label['image'] = photo_list[self.frame_number]
        self.video_label.image = photo_list[self.frame_number]
        show_num_frames_label(self)
        threading.Thread(target=update_total_frames_thread, args=(self,)).start()
        threading.Thread(target=unlock_skip_n_btn_thread, args=(self,)).start()
    except AttributeError:
        return


def unlock_skip_n_btn_thread(self):
    while save_sequence_thread.is_alive():
        try:
            if len(photo_list)-self.frame_number > self.skip_frames:
                self.next_detection['state'] = NORMAL
                self.skip5['state'] = NORMAL
                return
            time.sleep(0.1)
        except RuntimeError:
            return


def update_total_frames_thread(self):
    while save_sequence_thread.is_alive():
        try:
            current_frame = self.frame_number + 1
            total_frames = len(photo_list)

            to_display = '{}/{}'.format(current_frame, total_frames)
            self.num_frame_label['text'] = to_display
            time.sleep(0.1)
        except RuntimeError:
            return

    current_frame = self.frame_number + 1
    total_frames = len(photo_list)
    to_display = '{}/{}'.format(current_frame, total_frames)
    self.num_frame_label['text'] = to_display


# thread for showing total detections and current detection number
def show_num_frames_label(self):
    current_frame = self.frame_number + 1
    total_frames = len(photo_list)

    to_display = '{}/{}'.format(current_frame, total_frames)
    self.num_frame_label['text'] = to_display


# Accepts one parameter - to_check->Thread
# shows progress bar until all the frames of the video are saved
# returns void
def progress_bar_thread_func(to_check, self):
    global stop_all_thread
    if stop_all_thread:
        return

    def on_closing():
        return

    progress_bar_window = Toplevel()
    progress_bar_window.geometry('200x60')
    progress = Progressbar(progress_bar_window, orient=HORIZONTAL, length=100, mode='indeterminate')
    progress.pack()
    progress_bar_window.protocol("WM_DELETE_WINDOW", on_closing)
    processing_text = Label(progress_bar_window, text='Processing Video ...')
    processing_text.pack()

    try:
        def progress_bar_update():
            processing_text_counter = 0
            while to_check.is_alive():
                if stop_all_thread:
                    return
                progress['value'] = processing_text_counter % 100
                time.sleep(self.progress_bar_speed)
                processing_text_counter += 2
            progress['value'] = 100
            processing_text['text'] = 'Almost Done'
            time.sleep(.2)

        progress_bar_update()
        progress_bar_window.destroy()

    finally:
        self.close_btn['state'] = NORMAL
        return


# this functions handles different events related to slideshow
# also responsible for stopping the slide_show
def slide_show(self):
    global slideshowThread
    global photo_list
    global stop_slideshow

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
        threading.Thread(target=show_frame, args=(self,)).start()
        return

    self.slideshow_btn.config(text='Pause')
    self.video_label.pack_forget()
    self.slideshow_label.pack()
    self.fast_btn['state'] = NORMAL
    self.slow_btn['state'] = NORMAL
    self.rabbit_btn['state'] = NORMAL
    self.turtle_btn['state'] = NORMAL
    slideshowThread = threading.Thread(target=slideshow_thread, args=(self,))
    slideshowThread.start()


# this functions wait for specified time before showing next frame
def slideshow_thread(self):
    global photo_list
    global slideshowThread
    global stop_slideshow
    num_photos = len(photo_list)
    self.previous_detection['state'] = NORMAL
    global stop_all_thread

    while self.frame_number < num_photos:
        show_num_frames_label(self)
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
        self.turtle_btn['state'] = DISABLED
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
    if self.delay > self.lowest_slideshow_delay:
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
    if self.delay < self.highest_slideshow_delay:
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
    self.delay = self.highest_slideshow_delay
    self.slow_btn['state'] = DISABLED
    self.turtle_btn['state'] = DISABLED


def fastest(self):
    global stop_all_thread
    if stop_all_thread:
        return
    self.slow_btn['state'] = NORMAL
    self.turtle_btn['state'] = NORMAL
    self.delay = self.lowest_slideshow_delay
    self.fast_btn['state'] = DISABLED
    self.rabbit_btn['state'] = DISABLED


def stop_threads(self):
    global stop_all_thread
    stop_all_thread = True
    self.destroy()
