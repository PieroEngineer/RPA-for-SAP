from datetime import datetime
import threading
from queue import Queue
import time
import pythoncom
from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QButtonGroup

from models.config_model import ConfigModel
from models.data_model import DataModel
from models.rpa_model import RpaModel
from models.sap_model import SapModel
# from models.ocr_model import OcrModel # Use it if your company doesn't block APIs

from views.main_window import MainWindow

from utils.date_helper import subtract_n_days

## Let user modify the internal SAP element's codes
## Maybe include in the program a "block mouse" only when RPA is running

class RpaController(QObject):
    def __init__(self, data_model: DataModel, config_model: ConfigModel, view: MainWindow, app_controller):
        super().__init__()

        self.data_queue = Queue()

        self.app_controller = app_controller

        # View
        self.view = view

        # Models
        self.data_model = data_model
        self.config_model = config_model

        # UI Initialization
        self.ui_initialization()
        
        # Connections
        self.view.start_extraction_button.clicked.connect(self.on_run_rpa_clicked)
        self.view.adaptation_button.clicked.connect(self.app_controller.on_data_selection_window_open)

    # --- Complementary methods ---------
    def on_run_rpa_clicked(self):

        self.starting_time = datetime.now()

        self.view.start_extraction_button.setEnabled(False)
        self.view.adaptation_button.setEnabled(False)

        # Save config in json
        self.retrieve_input_settings_from_ui()

        # try:
        self.sap_model = SapModel(self.view.user_name_input.text(), self.view.user_password_input.text())
        current_sessions = self.sap_model.get_sessions()
        self.sap_model.order_windows_in_main_screen()
        self.rpa_model = RpaModel()
 
        self.run_rpa(current_sessions)

        self.end_time = datetime.now()

        print(f'⏱️  The extraction lasted {(self.end_time - self.starting_time).total_seconds()//60} minutes and {(self.end_time - self.starting_time).total_seconds()%60} seconds')

        self.config_model.generate_backup()
        self.data_model.generate_backup()
        
        self.data_model.write_date_in_backup_metadata(self.config_model.get_dates())

        if self.view.full_work_checkbox.isChecked():
            self.app_controller.on_rpa_finalized()

        self.data_model.reset_columns()

        self.view.start_extraction_button.setEnabled(True)
        self.view.adaptation_button.setEnabled(True)

        # except Exception as e:
        #     print(f"‼️  Process failed: {e}\n")


    # --- Main methods ---------
    def run_rpa(self, sessions):

        print(f"🤖  RPA started\n")

        current_config = self.config_model.get_config()

        for submanagment in current_config['Subgerencias de transmisión']:

            self.start_parallel_extraction(sessions, current_config, submanagment)

            if current_config['Incluir mes atrás']:
                print(f"🔙  Going a month back\n")

                mod_current_config = current_config.copy()
                new_initial_date, new_final_date = self.config_model.go_back_dates(mod_current_config['Fecha inic. Plan Trab.'])
                
                mod_current_config['Fecha inic. Plan Trab.'] = new_initial_date
                mod_current_config['Fecha fin. Plan Trab.'] = new_final_date

                self.start_parallel_extraction(sessions, mod_current_config, submanagment, True)

        print(f"✅🤖  RPA finishe, now verifing remining tasks...\n")


    def start_parallel_extraction(self, sessions: list, current_config: dict[str], submanagment: str, go_back_on_time = False):
        # The first one get the number of elements
        self.rpa_model.navigate_to_transaction(self.rpa_model.elements[''], 'zpm_pt', sessions[0]) ##
        # if go_back_on_time:#X
        #     current_config['Fecha fin. Plan Trab.'] = subtract_n_days(current_config['Fecha inic. Plan Trab.'], 1)
        #     current_config['Fecha inic. Plan Trab.'] = subtract_n_days(current_config['Fecha inic. Plan Trab.'], 31)
            
        self.rpa_model.access_filters(current_config, submanagment, sessions[0], go_back_on_time)
        
        first_table_object = self.rpa_model.generate_sap_object(self.rpa_model.elements[''], sessions[0])
        
        n_maintenances = first_table_object.RowCount
        n_sessions = len(sessions)

        for _ in range(2):##
            self.rpa_model.click_btn(self.rpa_model.elements[''], sessions[0])##

        print(f"🔎  maintenances: {n_maintenances}  |   sessions: {n_sessions}\n")

        # Divide rows among sessions
        avg = n_maintenances // n_sessions
        ranges = []
        for i in range(n_sessions):
            start = i * avg
            end = n_maintenances if i == n_sessions - 1 else (i + 1) * avg

            print(f'🔎🍕  the session number {i+1} takes from row {start} to row {end-1}\n')
            ranges.append(range(start, end))

        threads = []
        for i, session in enumerate(sessions):
            # CRITICAL: Marshal the session for the new thread
            session_stream = pythoncom.CoMarshalInterThreadInterfaceInStream(
                pythoncom.IID_IDispatch, session
            )
            
            t = threading.Thread(
                target=session_worker, 
                args=(current_config, submanagment, self.rpa_model, self.sap_model, (i, session_stream), ranges[i], self.data_queue)
            )
            threads.append(t)
            t.start()

        # Monitor the Queue while threads work
        # This keeps the controller 'alive' and processing data in real-time
        while any(t.is_alive() for t in threads) or not self.data_queue.empty():
            while not self.data_queue.empty():
                item = self.data_queue.get()
                self.on_one_data_ready(item)
            time.sleep(0.1)

        for t in threads:
            t.join()
        
        print("Parallel Extraction Complete.")
        

    # --- UI controlling methods ---------
    def ui_initialization(self):
        saved_config = self.config_model.get_config()
        
        self.view.user_name_input.setText(saved_config['Usuario'])
        self.view.user_password_input.setText(saved_config['Contraseña'])

        for button in self.view.state_button_group.buttons():
            if button.text() == saved_config['Estado de plan de trabajo']:
                button.setChecked(True)

        for button in self.view.department_button_group.buttons():
            if button.text() in saved_config['Subgerencias de transmisión']:
                button.setChecked(True)

        self.view.premonth_yes_rb.setChecked(saved_config['Incluir mes atrás'])
        self.view.premonth_no_rb.setChecked(not saved_config['Incluir mes atrás'])

        self.view.initial_data.set_datetime(datetime.strptime(saved_config["Fecha inic. Plan Trab."], "%d.%m.%Y"))
        self.view.final_data.set_datetime(datetime.strptime(saved_config["Fecha fin. Plan Trab."], "%d.%m.%Y"))

        self.view.full_work_checkbox.setChecked(True)

    def retrieve_input_settings_from_ui(self):
        settings_by_user = {}
        
        settings_by_user['Usuario'] = self.view.user_name_input.text()
        settings_by_user['Contraseña'] = self.view.user_password_input.text()

        settings_by_user['Estado de plan de trabajo'] = self.view.state_button_group.checkedButton().text()

        settings_by_user['Subgerencias de transmisión'] = self.get_checked_boxes(self.view.department_button_group)

        settings_by_user['Incluir mes atrás'] = self.view.premonth_yes_rb.isChecked()

        settings_by_user['Fecha inic. Plan Trab.'] = self.view.initial_data.get_selected_date()
        settings_by_user['Fecha fin. Plan Trab.'] = self.view.final_data.get_selected_date()

        self.config_model.set_config(settings_by_user)
        self.config_model.update_config(settings_by_user)

    def get_checked_boxes(self, button_group: QButtonGroup):
        checked_items = []
        # buttons() returns QAbstractButton widgets in the group
        for button in button_group.buttons():
            if button.isChecked():
                # For checkboxes, you might want their text or ID
                checked_items.append(button.text())
        
        if not checked_items:
            checked_items = ['RP01']
            print(f'⚠️ There were not checked items\n')

        return checked_items        

    # --- Methods called asynchronously ---------
    def on_one_data_ready(self, current_data: dict[str, str]):

        self.data_model.add_element_to_data(current_data)

        print(f'✅  Data saved \n')


def session_worker(current_config: dict[str], submanagment: str, rpa_model: RpaModel, sap_model: SapModel, i_session_stream, row_range, data_queue: Queue):
    """
    Individual thread logic.
    session_stream: The marshalled SAP session pointer.
    """
    # Initialize COM for this specific thread
    pythoncom.CoInitialize()
    try:
        # Unmarshal the session so this thread can use it

        session = sap_model.unmarshal_session(
            pythoncom.CoGetInterfaceAndReleaseStream(
                i_session_stream[1], pythoncom.IID_IDispatch
            )
        )

        # Selecting asset
        rpa_model.navigate_to_transaction(rpa_model.elements[''], 'zpm_pt', session) ##

        rpa_model.access_filters(current_config, submanagment, session) ##

        # Execute your extraction logic
        for row in row_range:
            table_object = rpa_model.generate_sap_object(rpa_model.elements[''], session)
            
            rpa_model.select_table_row_item(table_object, row)

            result = rpa_model.extract_data_from_one_maintenance(session)
            print(f'🔎  Result from the session number {i_session_stream[0]+1} emited')

            # Send data to the Controller's queue
            data_queue.put(result)

            rpa_model.click_btn(rpa_model.elements[''], session)
        
        # Going to the initial interface
        for _ in range(2):##
            rpa_model.click_btn(rpa_model.elements[''], session)
            
    finally:
        pythoncom.CoUninitialize()