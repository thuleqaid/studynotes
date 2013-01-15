import simplegui.simplegui_qt as simplegui

class TestApp(simplegui.BasicApp):
    def gengui(self):
        self.window=simplegui.SimpleWindow()
        self.window.setTitle("Bare")
        self.window.setSize(200,100)
        print(self.window.getTitle())
        print(self.window.getSize())

if __name__=='__main__':
    app=TestApp()
    app.run()