# -*- coding: utf-8 -*-
import simplegui as uim
ui=uim.UiManage('QT4')
#ui=uim.UiManage('WX')
#ui=uim.UiManage('GTK2')

class TestApp(ui.uiClass('BasicApp')):
    def build(self):
        self.window=ui.uiClass('SimpleWindow')()
        self.window.setTitle(u'見舞い')
        self.window.setCbCloseAction((TestApp.close,self,123))
        layout=ui.uiClass('BoxLayout')(ui.uiClass('BoxLayout').HORIZONTAL)
        btn1=ui.uiClass('Button')(self.window,"btn1")
        btn2=ui.uiClass('Button')(self.window,"btn2")
        layout.add(btn1)
        layout.add(btn2)
        layout2=ui.uiClass('GridLayout')(3,3)
        layout2.add(layout,0,0,1,3)
        btn3=ui.uiClass('Button')(self.window,"btn3")
        btn4=ui.uiClass('Button')(self.window,"btn4")
        label=ui.uiClass('Label')(self.window,u"ラベル")
        label2=ui.uiClass('Label')(self.window,u"ラベル")
        lineedit=ui.uiClass('TextEntry')(self.window,u"ラベル")
        btn1.setCbClick((TestApp.btn1click,self,btn3))
        btn2.setCbClick((TestApp.btn2click,self,btn4))
        btn3.setCbClick((TestApp.btn3click,self,3))
        btn4.setCbClick((TestApp.btn4click,self,btn4))
        lineedit.setCbFocusIn((TestApp.lineeditfocus,self,lineedit,' in'))
        lineedit.setCbFocusOut((TestApp.lineeditfocus,self,lineedit,' out'))
        lineedit.setCbTextEdited((TestApp.lineeditfocus,self,lineedit,' edit'))
        lineedit.setCbReturnPressed((TestApp.lineeditfocus,self,lineedit,' return'))
        layout2.add(btn3,1,0)
        layout2.add(btn4,1,2)
        layout2.add(label,1,1)
        layout2.add(label2,2,0)
        layout2.add(lineedit,2,1,1,2)
        self.window.setLayout(layout2)
        self.window.setSize(0,0)
        print(self.window.getTitle().decode('UTF8'))
        print(self.window.getSize())
        return self.window
    def btn1click(self,widget):
        if widget.getEnabled():
            widget.setEnabled(False)
        else:
            widget.setEnabled(True)
    def btn2click(self,widget):
        widget.setTitle("btn2Effect")
    def btn3click(self,n):
        print("btn3 "+str(n))
    def btn4click(self,widget):
        print(widget.getTitle().decode('UTF8'))
    def lineeditfocus(self,widget,state):
        print(widget.getTitle().decode('UTF8')+str(state))
    def close(self,n):
        print("close "+str(n))
if __name__=='__main__':
    app=TestApp()
    app.run()
