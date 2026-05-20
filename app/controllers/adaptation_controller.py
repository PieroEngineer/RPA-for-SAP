from datetime import datetime

from PyQt6.QtCore import QObject

from views.data_selection_window import DataSelectionWindow

from models.adaptation_model import AdaptationModel
from models.data_model import DataModel
from models.bases_model import BasesModel
from models.config_model import ConfigModel

class AdaptationController(QObject):
    def __init__(self, data_model: DataModel, config_model: ConfigModel, view: DataSelectionWindow, app_controller):
        super().__init__()

        self.app_controller = app_controller

        self.config_model = config_model
        self.data_model = data_model
        self.base_model = BasesModel()

        self.view = view

        self.base_model.load_base_data_by_cache()

        if any(base.empty for base in self.base_model.get_base_data()):
            self.update_message_about_bases()
            ## Let know about the main window about the issue
        else:
            self.update_message_about_bases(self.config_model.get_last_updating_datetime())

        self.view.timer.timeout.connect(self.clear_message)

        self.view.adapt_button.clicked.connect(lambda: self.on_adaptation_started(True))

        self.view.update_bases_button.clicked.connect(lambda: self.update_bases(self.view.source_selection_switch.switch.isChecked()))

        self.view.source_selection_switch.switch.toggled.connect(self.toggle_base_source)

    def toggle_base_source(self):
        if self.view.credentials_widget.isVisible():
            self.view.credentials_widget.hide()
        else:
            self.view.credentials_widget.show()

    def update_message_about_bases(self, update_datetime = ""):
        if update_datetime:
            if update_datetime == 'undefinite':
                self.view.last_base_updating_label.setText('✅  Se encontraron las bases para el COES y EQUIPOS')
            else:
                self.view.last_base_updating_label.setText('✅  La última actualización de las bases fue\n' + update_datetime)
        else:
            self.view.last_base_updating_label.setText('⚠️  No se han encontrado el excel con las bases del COES y EQUIPOS')


    def on_adaptation_started(self, is_direct = False):

        print(f"🔰  Starting adaptation...\n")
        self.starting_time = datetime.now()

        self.adaptation_model = AdaptationModel()

        if not is_direct:
            #X self.base_model.load_base_data_by_cache()
            self.adaptation_model.load_base_data(*self.base_model.get_base_data())
            
            self.adaptation_model.set_input_dates(self.data_model.read_dates_in_backup_metadata())
            self.adaptation_model.adapt_extracted_data(self.data_model.get_data())
        else:
            selected_checkbox = self.view.button_group.checkedButton()
            if selected_checkbox:
                #X self.base_model.load_base_data_by_cache()

                self.data_model.reassign_backup_path(selected_checkbox.text())
                self.data_model.recover_backup()

                self.adaptation_model.set_input_dates(self.data_model.read_dates_in_backup_metadata())
                self.adaptation_model.adapt_extracted_data(self.data_model.get_data())

        self.end_time = datetime.now()
        print(f'⏱️  The adaptation lasted {(self.end_time - self.starting_time).total_seconds()} seconds')

        self.adaptation_model.generate_excel()

    def update_bases(self, from_online = False):
        print(f'🧩  Is the source online? {from_online}\n')
        
        source_extractor = lambda: False

        if from_online:
            current_email =  self.view.email_input.text().strip()
            current_password = self.view.password_input.text().strip()

            if current_email and current_password:
                self.base_model.update_credentials(current_email, current_password)
                source_extractor = self.base_model.load_base_data_by_remote_file
            else:
                self.show_temporal_message(f'Se deben completar las credenciales', False)
        else:
            source_extractor = self.base_model.load_base_data_by_local_file

        if source_extractor():
            last_updating_datetime = self.base_model.get_last_updating_datetime()

            self.update_message_about_bases(last_updating_datetime)
            self.config_model.update_last_update_datetime(last_updating_datetime)

            self.show_temporal_message("Bases guardadas")
        else:
            self.show_temporal_message(f"Hubo un problema al guardar las bases desde {'local' if not from_online else 'remoto'}", False)

    def on_update_element_list(self):
        self.view.update_element_list(self.data_model.get_backup_references(True))

    def clear_message(self):
        """Hides the message label."""
        self.view.message_label.hide()

    def show_temporal_message(self, message, is_positive = True):
        """Displays a message temporarily."""
        self.view.message_label.setText(message)
        self.view.message_label.setStyleSheet(f"color: white; background-color: {"green" if is_positive else "orange"}; padding: 5px;")
        self.view.message_label.show()
        self.view.timer.start(3000)