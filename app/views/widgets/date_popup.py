
# date_popup_demo.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QDateEdit, QPushButton, QLabel
)
from PyQt6.QtCore import QDate
from PyQt6.QtCore import QLocale

from datetime import datetime

class DatePopup(QWidget):
    def __init__(self, date_name):
        super().__init__()

        self.root_layout = QVBoxLayout(self)

        self.peru_locale = QLocale(QLocale.Language.Spanish, QLocale.Country.Peru)
        self.fmt = "dd.MM.yyyy"

        # --- DateEdit with popup calendar ---

        self.name_lbl = QLabel(date_name)
        
        self.date_edit = QDateEdit(self)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate()) # default: today
        self.date_edit.setDisplayFormat(self.fmt)             

        # Set locale (affects month/day names in popup)
        self.date_edit.setLocale(self.peru_locale)

        # Buttons to demonstrate programmatic control
        self.btn_today = QPushButton("Establecer hoy")
        self.btn_next_week = QPushButton("Una semana después")

        self.btn_today.clicked.connect(self.set_today_)
        self.btn_next_week.clicked.connect(self.next_week_)

        self.buttons = QHBoxLayout()
        self.buttons.addWidget(self.btn_today)
        self.buttons.addWidget(self.btn_next_week)

        self.root_layout.addWidget(self.name_lbl)
        self.root_layout.addWidget(self.date_edit)
        self.root_layout.addLayout(self.buttons)

    # --- Handlers ---

    def set_today_(self):
        self.date_edit.setDate(QDate.currentDate())

    def next_week_(self):
        self.date_edit.setDate(self.date_edit.date().addDays(7))

    def set_day(self, date_str: str):
        qdate = self.peru_locale.toDate(date_str, self.fmt)
        self.date_edit.setDate(qdate)
    
    def get_selected_date(self):
        return self.date_edit.date().toString(self.fmt)
    
    def set_datetime(self, new_datetime: datetime):
        self.date_edit.setDate(QDate(new_datetime.year, new_datetime.month, new_datetime.day))