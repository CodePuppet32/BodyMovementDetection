from tkinter import messagebox
import window_skelton


def on_closing():
    messagebox.showwarning("Caution", "Use Close button to Exit")
    return


mainWin = window_skelton.WindowSkeleton()
mainWin.protocol("WM_DELETE_WINDOW", on_closing)
mainWin.mainloop()
