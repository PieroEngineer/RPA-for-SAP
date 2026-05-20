from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QAbstractButton
from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtProperty, QEasingCurve
from PyQt6.QtGui import QPainter, QColor

class SlidingSwitch(QAbstractButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 30)
        self.setCheckable(True)
        self._handle_position = 3  # Initial X position of the toggle circle
        
        # Setup sliding animation
        self.animation = QPropertyAnimation(self, b"handle_position", self)
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    @pyqtProperty(int)
    def handle_position(self):
        return self._handle_position

    @handle_position.setter
    def handle_position(self, pos):
        self._handle_position = pos
        self.update()

    def nextCheckState(self):
        self.setChecked(not self.isChecked())

    def setChecked(self, checked):
        super().setChecked(checked)
        # Animate from current position to end (33px) or start (3px)
        self.animation.stop()
        self.animation.setEndValue(33 if checked else 3)
        self.animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background Track
        track_color = QColor("#4CAF50") if self.isChecked() else QColor("#CCCCCC")
        painter.setBrush(track_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 15, 15)
        
        # Sliding Handle (The Circle)
        painter.setBrush(QColor("white"))
        painter.drawEllipse(self._handle_position, 3, 24, 24)

class LabeledSwitch(QWidget):
    """A wrapper widget that places labels on both sides of the switch"""
    def __init__(self, label_left="Off", label_right="On"):
        super().__init__()
        layout = QHBoxLayout(self)
        
        self.lbl_left = QLabel(label_left)
        self.switch = SlidingSwitch()
        self.lbl_right = QLabel(label_right)
        
        # Connect toggle signal to update visual feedback
        self.switch.toggled.connect(self._update_styles)
        
        layout.addWidget(self.lbl_left)
        layout.addWidget(self.switch)
        layout.addWidget(self.lbl_right)
        self._update_styles(False)

    def _update_styles(self, checked):
        # Visually emphasize the active option
        font_on = self.lbl_right.font()
        font_off = self.lbl_left.font()
        font_on.setBold(checked)
        font_off.setBold(not checked)
        self.lbl_right.setFont(font_on)
        self.lbl_left.setFont(font_off)
