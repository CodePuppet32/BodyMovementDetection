from tkinter import messagebox
import cv2
import classification_module
from helper_functions import *
from PIL import Image
from PIL import ImageTk


def show_photo(self):
    image_path = get_image_path()
    if image_path == '':
        messagebox.showerror('Empty Path', 'Path to image cannot be empty')
        return

    img_name = image_path.split('\\')[-1]
    image = cv2.imread(image_path)
    image = cv2.resize(image, dsize=(600, 450))

    self.video_frame.place_forget()
    self.webcam_frame.place_forget()
    self.image_frame.place(x=0, y=0, relheight=1, relwidth=1)

    detection_directory = 'detections\\photos\\'
    create_directory(detection_directory)

    classification_module.save_detection(image, detection_directory + img_name)
    image = ImageTk.PhotoImage(Image.fromarray(image[:, :, ::-1]))

    self.image_frame['image'] = image
    self.image_frame.image = image
