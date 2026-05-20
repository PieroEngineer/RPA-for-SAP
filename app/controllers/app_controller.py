import sys

from PyQt6.QtWidgets import QApplication

from models.config_model import ConfigModel
from models.data_model import DataModel

from views.main_window import MainWindow
from views.data_selection_window import DataSelectionWindow

from controllers.rpa_controller import RpaController
from controllers.adaptation_controller import AdaptationController

class AppController:
    def __init__(self, app: QApplication):
        self.app = app

        self.data_model = DataModel()
        self.config_model = ConfigModel()

        self.main_view = MainWindow()
        self.adaptation_view = DataSelectionWindow()

        self.adaptation_controller = AdaptationController(self.data_model, self.config_model, self.adaptation_view, self)
        self.rpa_controller = RpaController(self.data_model, self.config_model, self.main_view, self)

    def run(self):
        self.main_view.show()
        sys.exit(self.app.exec())

    def on_rpa_finalized(self):
        print(f'✅  RPA finished, starting next tasks...\n')

        self.adaptation_controller.on_adaptation_started()

    def on_data_selection_window_open(self):
        self.adaptation_controller.on_update_element_list()
        self.adaptation_view.exec()