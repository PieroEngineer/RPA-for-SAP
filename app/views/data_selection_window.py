from PyQt6.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QHBoxLayout, QScrollArea, QRadioButton, QPushButton, QButtonGroup, QDialog, QLabel
from views.widgets.labeled_switch import LabeledSwitch
from PyQt6.QtCore import Qt, QTimer

class DataSelectionWindow(QDialog):
    """
    A custom PyQt6 window with a scrollable frame for exclusive selection 
    of items (name, path tuples) and three action buttons.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Selección de datos extraídos")
        self.setGeometry(100, 100, 800, 500)

        # Main widget and layout
        self.main_layout = QHBoxLayout()

        self.selection_layout = QVBoxLayout()
        self.config_layout = QVBoxLayout()

        self.main_layout.addLayout(self.selection_layout)
        self.main_layout.addLayout(self.config_layout)

        # --- Scrollable Frame for Elements ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True) # Allows the widget inside to resize with the scroll area

        # Widget to hold the radio buttons inside the scroll area
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop) # Align items to the top
        self.scroll_content.setLayout(self.scroll_layout)
        
        self.scroll_area.setWidget(self.scroll_content)
        
        # Add the scroll area to the main layout
        self.selection_layout.addWidget(self.scroll_area)

        # --- Button Group for Exclusive Selection ---
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True) # Only one button can be checked at a time

        # --- Buttons at the Bottom ---
        self.button_layout = QVBoxLayout()

        self.update_bases_ui()

        self.delete_button = QPushButton("Borrar  🗑️")
        self.adapt_button = QPushButton("Iniciar\nAdaptación\n🔰")

        self.button_layout.addLayout(self.update_base_button_layout)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addWidget(self.adapt_button)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True) # The timer should run only once

        self.config_layout.addLayout(self.button_layout)

        self.message_label = QLabel()
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.hide()

        self.selection_layout.addWidget(self.message_label)

        # --- Updating base label
        self.last_base_updating_label = QLabel()
        self.selection_layout.addWidget(self.last_base_updating_label)

        self.setLayout(self.main_layout)

    def update_bases_ui(self):
        # First layout
        self.update_base_button_layout = QHBoxLayout()

        self.source_selection_layout = QVBoxLayout()
        self.credentials_widget = QWidget()
        self.credentials_layout = QVBoxLayout(self.credentials_widget)

        self.update_base_button_layout.addLayout(self.source_selection_layout)
        self.update_base_button_layout.addWidget(self.credentials_widget)

        self.credentials_widget.hide()

        # Decision layout
        self.update_bases_button = QPushButton("Actualizar bases  🔄️")
        self.source_selection_switch = LabeledSwitch('Localmente\n📂', 'Remotamente\n🔭')

        self.source_selection_layout.addWidget(self.update_bases_button)
        self.source_selection_layout.addWidget(self.source_selection_switch)

        # Credential layout
        self.email_access_layout = QHBoxLayout()
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email...")
        self.email_company_label = QLabel('@com.pe')
        self.email_access_layout.addWidget(self.email_input)
        self.email_access_layout.addWidget(self.email_company_label)
        self.email_access_layout.addStretch(1)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña...")

        self.credentials_layout.addLayout(self.email_access_layout)
        self.credentials_layout.addWidget(self.password_input)

    def update_element_list(self, elements: list[str]):
        """
        Dynamically updates the list of checkable elements in the frame.
        """
        print(f'🖌️  Updating UI element list of data backups')

        # Remove existing widgets from the layout and button group
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                self.button_group.removeButton(widget)
                widget.setParent(None) # Remove from layout
                widget.deleteLater() # Schedule for deletion

        # Add new radio buttons to the layout and button group
        for name in elements:
            radio_button = QRadioButton(name)
            # Store the associated path as a custom property
            radio_button.setProperty("element_name", name) 
            self.scroll_layout.addWidget(radio_button)
            self.button_group.addButton(radio_button)
        
        # Set the first button as checked by default if list is not empty
        if elements and self.button_group.buttons():
            self.button_group.buttons()[0].setChecked(True)