# -*- coding: utf-8 -*-
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
sys.path.append('..')
sys.path.append('../plugins')
from cparser import getTestFuncInfo
from driverparser import formatExcelText
sys.path.append('../ui')
import funcfinder_ui
from funcfinder_ui import _fromUtf8

class MyWindow(QMainWindow):
    def setupUi(self,ui):
        self._ui=ui
        self._ui.setupUi(self)
        self._fdict={}
        self._clip=QApplication.clipboard()
        self.show()
    def onBtnSrc(self):
        srcpath=QFileDialog.getExistingDirectory(self,_fromUtf8("Choose Input Source Folder"))
        self._ui.edit_src.setText(srcpath)
    def onBtnTok(self):
        tokpath=QFileDialog.getExistingDirectory(self,_fromUtf8("Choose Output Token Folder"))
        self._ui.edit_tok.setText(tokpath)
    def onBtnFind(self):
        srcpath=self._ui.edit_src.text()
        tokpath=self._ui.edit_tok.text()
        func=self._ui.edit_func.text()
        self._fdict=getTestFuncInfo(srcpath,tokpath,func)
        lw=self._ui.listWidget
        lw.clear()
        if len(self._fdict[func])>0:
            for finfo in self._fdict[func]:
                lw.insertItem(lw.count(),'%s\t%s'%(_fromUtf8(finfo['decl']),_fromUtf8(finfo['srcfile'])))
        else:
            lw.insertItem(0,_fromUtf8("Cannot found the function"))
    def onBtnOutput(self):
        idx=self._ui.listWidget.currentRow()
        if idx<0:
            idx=0
        fkeys=list(self._fdict.keys())
        if len(fkeys)!=1:
            # no function searched
            return
        func=fkeys[0]
        finfo=self._fdict[func]
        if len(finfo)<=0:
            # function not found
            return
        self.formatTxt(func,finfo[idx])
    def onMenu(self,action):
        menutxt=action.text()
        if menutxt=='Exit':
            self.close()
    def formatTxt(self,funcname,finfo):
        outtxt=formatExcelText(funcname,finfo)
        self._clip.setText(_fromUtf8(outtxt))
        QMessageBox.information(self,_fromUtf8("Output"),_fromUtf8("Copied into Clipboard"))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow=MyWindow()
    mainwindow.setupUi(funcfinder_ui.Ui_MainWindow())
    app.exec_()
