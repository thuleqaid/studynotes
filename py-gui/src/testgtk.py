import simplegui.simplegui_gtk as simplegui

class TestApp(simplegui.BasicApp):
    def gengui(self):
        self.window=simplegui.SimpleWindow()
        self.window.setTitle("Bare")
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
        layout2.add(btn3,1,0)
        layout2.add(btn4,1,2)
        self.window.setLayout(layout2)
        self.window.setSize(0,0)
        print(self.window.getTitle())
        print(self.window.getSize())
    def close(self,n):
        print("close "+str(n)+"\n")
if __name__=='__main__':
    app=TestApp()
    app.run()
