import os
from tkinter import *
from gloval_vars import *
from PIL import ImageTk, Image


def image_btn_(path):
    img = Image.open(path)
    img = img.resize((640, 480), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    image_label['image'] = img
    image_label.image = img


parent = Tk()
parent.geometry('1000x600')

left = 0.25
right = 1 - left

left_frame = Frame(parent, background='black')
photo_directory = 'detections/photos'
image_list = os.listdir(photo_directory)

my_canvas = Canvas(left_frame)
my_canvas.pack(side=RIGHT, fill=BOTH, expand=True)

my_scrollbar = Scrollbar(parent, orient=VERTICAL, command=my_canvas.yview)
my_scrollbar.pack(side=LEFT, fill=Y)

my_canvas.configure(yscrollcommand=my_scrollbar.set)
my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox('all')))

btn_frame = Frame(my_canvas)

my_canvas.create_window((0, 0), window=btn_frame, anchor=NW)

for i, image in enumerate(image_list):
    Button(btn_frame, default_button, width=24, text=image, command=lambda img=image: image_btn_(os.path.join(photo_directory, img)))\
        .grid(row=i, column=0, pady=5)


right_frame = Frame(parent, background='red')
image_label = Label(right_frame, background='white')
image_label.pack(padx=20, pady=20, fill=BOTH, expand=True)

left_frame.place(x=20, relheight=1, relwidth=left)
right_frame.place(relx=left, relheight=1, relwidth=right)

parent.mainloop()
