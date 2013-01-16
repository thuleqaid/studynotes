import simplegui.simplegui_gtk as simplegui

class TestApp(simplegui.BasicApp):
    def gengui(self):
        self.window=simplegui.SimpleWindow()
        self.window.setTitle("Bare")
        self.window.setSize(200,100)
        self.window.setCbCloseAction((TestApp.close,self,123))
        print(self.window.getTitle())
        print(self.window.getSize())
    def close(self,n):
        print("close "+str(n)+"\n")
if __name__=='__main__':
    app=TestApp()
    app.run()
