import simplegui.simplegui_wx as simplegui
import wx

class TestApp(simplegui.BasicApp):
    def gengui(self):
        self.window=wx.Frame(parent=None,title='Bare')

if __name__=='__main__':
    app=TestApp()
    app.run()
