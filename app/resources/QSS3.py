QSS = """
/********** General Styles **********/
* {
    font-family: "Segoe UI", Arial, sans-serif;
    color: #e0e0e0; /* Light gray text for a dark theme */
}

QWidget {
    background-color: #2c2c2c; /* Main background color */
}

/* Base style for QFrame and other containers */
QFrame, QGroupBox {
    background-color: #3c3c3c;
    border: 1px solid #5a5a5a;
    border-radius: 4px;
    margin: 5px;
    padding: 10px;
}

/* GroupBox title styling */
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0px 5px 0px 5px;
    color: #4da6ff; /* Accent color for titles */
    font-weight: bold;
}

QLabel {
    background-color: transparent; /* Labels usually shouldn't have a background */
    border: none;
    padding: 0;
}

/********** Input Widgets **********/
QLineEdit {
    background-color: #454545;
    border: 1px solid #5a5a5a;
    padding: 5px;
    border-radius: 4px;
    selection-background-color: #4da6ff;
    color: #e0e0e0;
}

QLineEdit:focus {
    border: 1px solid #4da6ff; /* Highlight color when focused */
}

/********** Buttons **********/
QPushButton {
    background-color: #4da6ff; /* Blue accent color */
    border: none;
    color: white;
    padding: 8px 16px;
    border-radius: 4px;
    margin: 5px;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #1a75ff; /* Slightly darker blue on hover */
}

QPushButton:pressed {
    background-color: #004dff; /* Even darker blue when pressed */
}

QPushButton:disabled {
    background-color: #5a5a5a;
    color: #9e9e9e;
}

/********** Checkboxes and Radio Buttons **********/
QCheckBox::indicator, QRadioButton::indicator {
    width: 16px;
    height: 16px;
    background-color: #454545;
    border: 1px solid #5a5a5a;
    border-radius: 3px;
}

QRadioButton::indicator {
    border-radius: 8px; /* Makes it a circle */
}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background-color: #4da6ff;
    border: 1px solid #4da6ff;
}

QCheckBox::indicator:checked:hover, QRadioButton::indicator:checked:hover {
    background-color: #1a75ff;
}

/********** Scroll Area **********/
QScrollArea {
    border: 1px solid #5a5a5a;
    background-color: #2c2c2c;
}

QScrollBar:vertical, QScrollBar:horizontal {
    border: none;
    background: #3c3c3c;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #5a5a5a;
    min-height: 20px;
    min-width: 20px;
    border-radius: 4px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
    height: 0px;
    width: 0px;
}
"""
