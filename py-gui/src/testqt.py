import simplegui.simplegui_qt as simplegui
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        dial = QDial()
        dial.setNotchesVisible(True)
        spinbox = QSpinBox()
        layout = QHBoxLayout()
        layout.addWidget(dial)
        layout.addWidget(spinbox)
        self.setLayout(layout)
        self.connect(dial, SIGNAL("valueChanged(int)"), spinbox.setValue)
        self.connect(spinbox, SIGNAL("valueChanged(int)"), dial.setValue)
        self.setWindowTitle("Signals and Slots")

class TestApp(simplegui.BasicApp):
    def gengui(self):
        self.window=Form()

if __name__=='__main__':
    app=TestApp()
    app.run()