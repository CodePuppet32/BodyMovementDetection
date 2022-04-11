import install_packages_module
import window_skelton


class MainWindow(window_skelton.WindowSkeleton):
    def __init__(self):
        super().__init__()


mainWin = MainWindow()
mainWin.mainloop()
