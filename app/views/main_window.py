from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QLineEdit, QWidget, QPushButton, QFrame, QLabel, QGroupBox, QRadioButton, QButtonGroup, QCheckBox

from views.widgets.date_popup import DatePopup

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RPA PRIME")
        self.setMinimumSize(1200, 300)
        self.setWindowFlags(Qt.WindowType.Window)

        # General elements
        self.main_layout = QVBoxLayout()

        self.user_layout = QHBoxLayout()
        self.thin_line_1 = QFrame()

        self.scope_layout = QHBoxLayout()
        self.thin_line_2 = QFrame()

        self.date_layout = QHBoxLayout()
        self.thin_line_3 = QFrame()

        self.decision_layout = QHBoxLayout()
        
        self.main_layout.addLayout(self.user_layout)
        self.main_layout.addWidget(self.thin_line_1)
        self.main_layout.addLayout(self.scope_layout)
        self.main_layout.addWidget(self.thin_line_2)
        self.main_layout.addLayout(self.date_layout)
        self.main_layout.addWidget(self.thin_line_3)
        self.main_layout.addLayout(self.decision_layout)

        # UI building
        self.user_ui()
        self.scope_ui()
        self.date_ui()
        self.decision_ui()

        for thin_line in [self.thin_line_1, self.thin_line_2, self.thin_line_3]:
            thin_line.setFrameShape(QFrame.Shape.HLine)
            thin_line.setFrameShadow(QFrame.Shadow.Sunken)
            thin_line.setLineWidth(1)

        # Set final layout
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

    def decision_ui(self):
        self.full_work_checkbox = QCheckBox('Adaptar datos inmediatamente\ndespués de extraerlos')
        self.start_extraction_button = QPushButton('🪝  Iniciar extración')
        self.adaptation_button = QPushButton('⚙️  Configurar adaptación')

        self.decision_layout.addWidget(self.full_work_checkbox)
        self.decision_layout.addWidget(self.start_extraction_button)
        self.decision_layout.addWidget(self.adaptation_button)


    def user_ui(self):
        self.user_name_lbl = QLabel('Usuario: ')
        self.user_name_input = QLineEdit()
        self.user_password_lbl =  QLabel('Contraseña: ')
        self.user_password_input = QLineEdit()

        self.user_layout.addWidget(self.user_name_lbl)
        self.user_layout.addWidget(self.user_name_input)
        self.user_layout.addStretch()
        self.user_layout.addWidget(self.user_password_lbl)
        self.user_layout.addWidget(self.user_password_input)

    def scope_ui(self):
        # Plan state part
        self.state_group = QGroupBox("Estado de plan de trabajo: ")
        self.state_group_layout = QVBoxLayout(self.state_group)

        self.state_3_rb = QRadioButton("03")
        self.state_4_rb = QRadioButton("04")
        self.state_3_4_rb = QRadioButton("03 - 04")

        self.state_group_layout.addWidget(self.state_3_rb)
        self.state_group_layout.addWidget(self.state_4_rb)
        self.state_group_layout.addWidget(self.state_3_4_rb)

        self.state_button_group = QButtonGroup(self)
        self.state_button_group.setExclusive(True)
        self.state_button_group.addButton(self.state_3_rb, 1)
        self.state_button_group.addButton(self.state_4_rb, 2)
        self.state_button_group.addButton(self.state_3_4_rb, 3)

        # Transmission deparment part
        self.department_group = QGroupBox("Subgerencias de transmisión: ")
        self.department_group_layout = QVBoxLayout(self.department_group)

        self.department_rp01_cb = QCheckBox("RP01")
        self.department_rp02_cb = QCheckBox("RP02")
        self.department_rp04_cb = QCheckBox("RP04")

        self.department_group_layout.addWidget(self.department_rp01_cb)
        self.department_group_layout.addWidget(self.department_rp02_cb)
        self.department_group_layout.addWidget(self.department_rp04_cb)

        self.department_button_group = QButtonGroup(self)
        self.department_button_group.setExclusive(False)
        self.department_button_group.addButton(self.department_rp01_cb, 1)
        self.department_button_group.addButton(self.department_rp02_cb, 2)
        self.department_button_group.addButton(self.department_rp04_cb, 3)

        # Pre-month part
        self.premonth_group = QGroupBox("Analizar adicionalmente fechas atrás")
        self.premonth_group_layout = QVBoxLayout(self.premonth_group)

        self.premonth_yes_rb = QRadioButton("Sí")
        self.premonth_no_rb = QRadioButton("No")

        self.premonth_group_layout.addWidget(self.premonth_yes_rb)
        self.premonth_group_layout.addWidget(self.premonth_no_rb)

        self.premonth_button_group = QButtonGroup(self)
        self.premonth_button_group.setExclusive(True)
        self.premonth_button_group.addButton(self.premonth_yes_rb, 1)
        self.premonth_button_group.addButton(self.premonth_no_rb, 2)

        # Inserting
        self.scope_layout.addWidget(self.state_group)
        self.scope_layout.addWidget(self.department_group)
        self.scope_layout.addWidget(self.premonth_group)

    def date_ui(self):
        self.initial_data = DatePopup('Ingrese fecha inicial')
        self.final_data = DatePopup('Ingrese fecha final')

        self.date_layout.addWidget(self.initial_data)
        self.date_layout.addWidget(self.final_data)