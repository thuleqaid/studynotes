# -*- coding: utf-8 -*-
import simplegui.simplegui_gtk as simplegui

class TestApp(simplegui.BasicApp):
    def gengui(self):
        self.window=simplegui.SimpleWindow()
        self.window.setTitle(u'見舞い')
        self.window.setCbCloseAction((TestApp.close,self,123))
        layout=simplegui.BoxLayout(simplegui.BoxLayout.HORIZONTAL)
        btn1=simplegui.Button(self.window,"btn1")
        btn2=simplegui.Button(self.window,"btn2")
        layout.add(btn1)
        layout.add(btn2)
        layout2=simplegui.GridLayout(2,3)
        layout2.add(layout,0,0,1,3)
        btn3=simplegui.Button(self.window,"btn3")
        btn4=simplegui.Button(self.window,"btn4")
        btn1.setCbClick((TestApp.btn1click,self,btn3))
        btn2.setCbClick((TestApp.btn2click,self,btn4))
        btn3.setCbClick((TestApp.btn3click,self,3))
        btn4.setCbClick((TestApp.btn4click,self,btn4))
        layout2.add(btn3,1,0)
        layout2.add(btn4,1,2)
        self.window.setLayout(layout2)
        self.window.setSize(0,0)
        print(self.window.getTitle().decode('UTF8'))
        print(self.window.getSize())
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
    def close(self,n):
        print("close "+str(n))
if __name__=='__main__':
    app=TestApp()
    app.run()
