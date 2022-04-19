from tkinter import *

window = Tk()

buttons = []


def position(pos):
    print(pos)


for i in range(7):
    buttons.append(Button(window, width=10, height=5, bg="red", command=lambda c=i: position(c)).grid(row=0, column=i))

window.mainloop()
