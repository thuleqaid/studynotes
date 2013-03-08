# -*- coding: utf-8 -*-
import sys
import random
import logging
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import memory_ui
logging.basicConfig(level=logging.CRITICAL)

class MyDialog(QDialog):
    def setupUi(self,ui):
        self._ui=ui
        self._ui.setupUi(self)
        self._maxnum,bret=self._ui.combo_max.itemText(self._ui.combo_max.count()-1).toInt()
        self._data=[0 for i in range(self._maxnum)]
        self._timer=QTimer()
        self._timercnt=0
        self.connect(self._timer,SIGNAL("timeout()"),self.timeout)
        self.show()
    def onBtnNew(self):
        self._ui.btn_new.setEnabled(False)
        self._ui.btn_end.setEnabled(True)
        self._ui.combo_min.setEnabled(False)
        self._ui.combo_max.setEnabled(False)
        self._ui.combo_cnt.setEnabled(False)
        self._ui.spin_inv.setEnabled(False)
        for i in range(len(self._data)):
            self._ui.__dict__["label_ans%d"%(i+1)].setText("<font color=gray>0</font>")
            self._ui.__dict__["combo_%d"%(i+1)].setEnabled(False)
            self._ui.__dict__["combo_%d"%(i+1)].setCurrentIndex(0)
        self.newGame()
        self.starttimer()
    def onBtnEnd(self):
        self._ui.btn_end.setEnabled(False)
        self._ui.btn_con.setEnabled(False)
        self._ui.btn_new.setEnabled(True)
        self._ui.combo_min.setEnabled(True)
        self._ui.combo_max.setEnabled(True)
        self._ui.combo_cnt.setEnabled(True)
        self._ui.spin_inv.setEnabled(True)
        self.stoptimer()
    def onBtnCon(self):
        self._ui.btn_con.setEnabled(False)
        self.starttimer()
    def onBtnShow(self):
        self._ui.btn_show.setEnabled(False)
        for i in range(len(self._data)):
            ans=self._ui.__dict__["label_ans%d"%(i+1)]
            uans=self._ui.__dict__["combo_%d"%(i+1)]
            if self._min<=i+1<=self._max:
                if self._cnt-self._data[i]==uans.currentText().toInt()[0]:
                    ans.setText("<font color=black>%d</font>"%(self._cnt-self._data[i]))
                else:
                    ans.setText("<font color=red>%d</font>"%(self._cnt-self._data[i]))
            else:
                ans.setText("<font color=gray>0</font>")
            uans.setEnabled(False)
        if len(self._numqueue)>0:
            self._ui.btn_con.setEnabled(True)
    def timeout(self):
        logging.debug("Timeout:TimerCnt(%d)"%(self._timercnt))
        self._timercnt-=1
        if self._timercnt<1:
            self.stoptimer()
            self._ui.btn_show.setEnabled(True)
            self._ui.label1.clear()
            self._ui.label2.clear()
            self._ui.label3.clear()
            self._ui.label4.clear()
            for i in range(len(self._data)):
                if self._min<=i+1<=self._max:
                    self._ui.__dict__["combo_%d"%(i+1)].setEnabled(True)
        else:
            self.starttimer()
    def starttimer(self):
        if self._timercnt<1:
            self._timercnt=random.randint(1,len(self._numqueue))
            logging.debug("Start Timer:Cnt(%d)"%self._timercnt)
            self._timer.start(self._inv*1000)
        self.dispNum()
    def stoptimer(self):
        self._timer.stop()
        self._timercnt=0
    def dispNum(self):
        nextnum=self.nextNum()
        lasttext=self._ui.label3.text()
        self._ui.label4.setText(lasttext.replace("black","gray"))
        self._ui.label3.setText(self._ui.label2.text())
        lasttext=self._ui.label1.text()
        self._ui.label2.setText(lasttext.replace("red","black"))
        self._ui.label1.setText("<font color=red>%d</font>"%(nextnum))
    def newGame(self):
        self._min=self._ui.combo_min.currentText().toInt()[0]
        self._max=self._ui.combo_max.currentText().toInt()[0]
        self._cnt =self._ui.combo_cnt.currentText().toInt()[0]
        self._inv =self._ui.spin_inv.value()
        logging.debug("MinNumber:%s"%(self._min))
        logging.debug("MaxNumber:%s"%(self._max))
        logging.debug("Interval:%s"%(self._inv))
        if self._max<self._min:
            self._max=self._maxnum
        self._numqueue=[]
        for i in range(self._maxnum):
            if self._min <= i+1 <= self._max:
                self._data[i]=self._cnt
                self._numqueue.extend([i for x in range(self._cnt)])
            else:
                self._data[i]=0
        logging.info(self._numqueue)
    def nextNum(self):
        if len(self._numqueue)<1:
            return -1
        random.shuffle(self._numqueue)
        ret=self._numqueue.pop()
        self._data[ret]-=1
        ret+=1
        return ret
    def enableCombos(self,enabled):
        pass
if __name__ == '__main__':
    app=QApplication(sys.argv)
    dialog=MyDialog()
    dialog.setupUi(memory_ui.Ui_Dialog())
    app.exec_()

