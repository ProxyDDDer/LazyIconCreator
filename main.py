import ctypes
from idlelib import window

from PIL import Image
from PySide6.QtWidgets import QApplication
import sys

from core.version import get_version
from pages.home_page import HomePage

# img = Image.open("image.png")

if __name__ == '__main__':
    print(f"LazyIconCreator {get_version()} has been launched.")
    # img.save("icon.ico", sizes=[(256,256)])

    # print("icon.ico saved")

    # Creating app and registering in system
    app = QApplication(sys.argv)

    # Open new start window
    window = HomePage()
    window.show()

    # Trying to set window icon
    try:
        appid = 'RED-IGLA.LazyIconCreator'
        shell32 = ctypes.windll.shell32
        set_id_func = getattr(shell32, 'SetCurrentProcessExplicitAppUserModelID', None)

        if set_id_func:
            set_id_func(appid)
    except (OSError, AttributeError):
        pass

    # Endless cycle
    sys.exit(app.exec())

