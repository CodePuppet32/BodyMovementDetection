import os
from tkinter import filedialog as fd


# empty -> whether new directory should be empty, True -> Empty - False -> Doesn't matter
def create_directory(path, empty=False):
    if empty and os.path.exists(path):
        for file in os.listdir(path):
            os.remove(os.path.join(path, file))
        return
    try:
        os.makedirs(path)
    except FileExistsError:
        return


def get_image_path():
    filetypes = (
        ('All files', '*.*'),
        ('jpg files', '*.jpg'),
        ('png files', '*.png')
    )

    image_name = fd.askopenfilename(filetypes=filetypes)
    # if user doesn't select any image
    if image_name == '':
        return ''
    # return absolute path
    image_path = os.path.abspath(image_name)
    return image_path


def get_video_path():
    filetypes = (
        ('All files', '*.*'),
        ('mp4 files', '*.mp4')
    )

    video_name = fd.askopenfilename(filetypes=filetypes)
    # if user doesn't select any file
    if video_name == '':
        return ''
    video_path = os.path.abspath(video_name)
    return video_path
