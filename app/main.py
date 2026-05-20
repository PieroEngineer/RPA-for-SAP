import sys

# import qasync
from PyQt6.QtWidgets import QApplication

from controllers.app_controller import AppController
from resources.QSS3 import QSS

__version__ = "1.0.0"
__author__ = "Piero Olivas"
__credits__ = ['Piero Olivas']
__maintainer__ = "Piero Olivas"
__email__ = "psot14022001@gmail.com"

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)

    # Application controller
    app_controller = AppController(app)
    app_controller.run()

if __name__ == "__main__":
    main()