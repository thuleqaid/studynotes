import simplegui.simplegui_wx as simplegui

class TestApp(simplegui.BasicApp):
    def gengui(self):
        self.window=simplegui.SimpleWindow()
        self.window.setTitle("Bare")
        self.window.setSize(200,100)
        layout=simplegui.BoxLayout(simplegui.BoxLayout.HORIZONTAL)
        btn1=simplegui.Button(self.window,"btn1")
        btn2=simplegui.Button(self.window,"btn2")
        layout.add(btn1)
        layout.add(btn2)
        self.window.setLayout(layout)
        print(self.window.getTitle())
        print(self.window.getSize())

if __name__=='__main__':
    app=TestApp()
    app.run()
