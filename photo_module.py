import threading
from tkinter import messagebox
import cv2
import classification_module
from helper_functions import *
from PIL import Image
import numpy as np
from PIL import ImageTk


def show_photo(self):
    image_path = get_image_path()
    if image_path == '':
        messagebox.showerror('Empty Path', 'Path to image cannot be empty')
        return

    threading.Thread(target=show_photo_thread, args=(self, image_path)).start()


def show_photo_thread(self, image_path):
    img_name = image_path.split('\\')[-1]
    image = cv2.imread(image_path)

    try:
        image = cv2.resize(image, dsize=(680, 550))
    except cv2.error:
        messagebox.showerror('Wrong File', 'Image is invalid')
        return

    self.video_frame.place_forget()
    self.webcam_frame.place_forget()
    self.image_frame.place(x=0, y=0, relheight=1, relwidth=1)

    img = Image.open(image_path)
    img = img.resize((680, 550), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    self.image_frame['image'] = img
    self.image_frame.image = img

    genre, image = classification_module.save_detection(image)

    if not genre:
        return

    self.sp.model_point_of_contact(genre)
    image = ImageTk.PhotoImage(Image.fromarray(image[:, :, ::-1]))
    self.image_frame['image'] = image
    self.image_frame.image = image
