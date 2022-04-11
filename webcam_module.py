import threading
import classification_module
from tkinter import messagebox
from PIL import ImageTk
from PIL import Image
import cv2
from helper_functions import *


# Accepts no parameter
# Returns void
def show_webcam(self):
    self.vid = cv2.VideoCapture(0)
    try:
        _, frame = self.vid.read()
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    except cv2.error:
        messagebox.showerror('Error', 'No Webcam Found')
        return
    create_directory('detections\\webcam\\')
    self.image_frame.place_forget()
    self.video_frame.place_forget()
    self.webcam_frame.place(x=0, y=0, relheight=1, relwidth=1)
    threading.Thread(target=self.start_webcam_feed, args=()).start()


# Accepts no parameter
# Returns void
def start_webcam_feed(self):
    counter = 0
    webcam_feed_save_path = 'DetectedImage\\webcam\\image'
    while 1:
        _, frame = self.vid.read()
        classification_module.save_detection(frame, webcam_feed_save_path)
        image = ImageTk.PhotoImage(Image.fromarray(frame[:, :, ::-1]))
        self.webcam_frame['image'] = image
        self.webcam_frame.image = image
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break
        counter += 1
    self.vid.release()
