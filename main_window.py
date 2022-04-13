import sys
from tkinter import messagebox

import install_packages_module
import window_skelton


def on_closing():
    return


mainWin = window_skelton.WindowSkeleton()
mainWin.protocol("WM_DELETE_WINDOW", on_closing)
mainWin.mainloop()
