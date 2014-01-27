# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'funcfinder.ui'
#
# Created: Mon Jan 20 17:14:53 2014
#      by: PyQt4 UI code generator 4.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(480, 320)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.edit_tok = QtGui.QLineEdit(self.centralwidget)
        self.edit_tok.setObjectName(_fromUtf8("edit_tok"))
        self.gridLayout.addWidget(self.edit_tok, 1, 1, 1, 1)
        self.edit_src = QtGui.QLineEdit(self.centralwidget)
        self.edit_src.setObjectName(_fromUtf8("edit_src"))
        self.gridLayout.addWidget(self.edit_src, 0, 1, 1, 1)
        self.btnTok = QtGui.QPushButton(self.centralwidget)
        self.btnTok.setObjectName(_fromUtf8("btnTok"))
        self.gridLayout.addWidget(self.btnTok, 1, 2, 1, 1)
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.listWidget = QtGui.QListWidget(self.centralwidget)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.gridLayout.addWidget(self.listWidget, 3, 0, 1, 3)
        self.edit_func = QtGui.QLineEdit(self.centralwidget)
        self.edit_func.setObjectName(_fromUtf8("edit_func"))
        self.gridLayout.addWidget(self.edit_func, 2, 1, 1, 1)
        self.btnSrc = QtGui.QPushButton(self.centralwidget)
        self.btnSrc.setObjectName(_fromUtf8("btnSrc"))
        self.gridLayout.addWidget(self.btnSrc, 0, 2, 1, 1)
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.btnFind = QtGui.QPushButton(self.centralwidget)
        self.btnFind.setObjectName(_fromUtf8("btnFind"))
        self.gridLayout.addWidget(self.btnFind, 2, 2, 1, 1)
        self.btnOutput = QtGui.QPushButton(self.centralwidget)
        self.btnOutput.setObjectName(_fromUtf8("btnOutput"))
        self.gridLayout.addWidget(self.btnOutput, 4, 2, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 480, 19))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionExti = QtGui.QAction(MainWindow)
        self.actionExti.setObjectName(_fromUtf8("actionExti"))
        self.menuFile.addAction(self.actionExti)
        self.menubar.addAction(self.menuFile.menuAction())
        self.label.setBuddy(self.edit_src)
        self.label_2.setBuddy(self.edit_tok)
        self.label_3.setBuddy(self.edit_func)

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.btnSrc, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.onBtnSrc)
        QtCore.QObject.connect(self.btnTok, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.onBtnTok)
        QtCore.QObject.connect(self.btnFind, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.onBtnFind)
        QtCore.QObject.connect(self.btnOutput, QtCore.SIGNAL(_fromUtf8("clicked()")), MainWindow.onBtnOutput)
        QtCore.QObject.connect(self.menubar, QtCore.SIGNAL(_fromUtf8("triggered(QAction*)")), MainWindow.onMenu)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.btnSrc, self.btnTok)
        MainWindow.setTabOrder(self.btnTok, self.btnFind)
        MainWindow.setTabOrder(self.btnFind, self.btnOutput)
        MainWindow.setTabOrder(self.btnOutput, self.edit_src)
        MainWindow.setTabOrder(self.edit_src, self.edit_tok)
        MainWindow.setTabOrder(self.edit_tok, self.edit_func)
        MainWindow.setTabOrder(self.edit_func, self.listWidget)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Function Finder", None))
        self.label.setText(_translate("MainWindow", "Source Files", None))
        self.btnTok.setText(_translate("MainWindow", "...", None))
        self.label_2.setText(_translate("MainWindow", "Token Files", None))
        self.btnSrc.setText(_translate("MainWindow", "...", None))
        self.label_3.setText(_translate("MainWindow", "Target Function", None))
        self.btnFind.setText(_translate("MainWindow", "Search", None))
        self.btnOutput.setText(_translate("MainWindow", "Output", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.actionExti.setText(_translate("MainWindow", "Exit", None))

