import PyQt4.QtGui as _QtGui

class BasicApp(object):
    def gengui(self):
        self.window=_QtGui.QDialog()
    def show(self):
        self.window.show()
    def run(self):
        app=_QtGui.QApplication([])
        self.gengui()
        self.show()
        app.exec_()
