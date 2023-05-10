from tkinter import *
from PIL import Image
from PIL import ImageTk


parent = Tk()
parent.geometry('400x400')

image_frame = Frame(parent)
image_frame.pack()

image_label = Label(image_frame)
image_label.pack(fill=BOTH, expand=True)
image_path = r"D:\V\Camera\New folder (2)\IMG_20211204_005504.jpg"
width = image_label.winfo_width()
height = image_label.winfo_height()
print(width, height)
img = Image.open(image_path)
img = img.resize((width, height), Image.ANTIALIAS)
img = ImageTk.PhotoImage(img)
image_label['image'] = img
image_label.image = img

parent.mainloop()
