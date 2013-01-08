import simplegui.simplegui_gtk as simplegui
import gtk

class TestApp(simplegui.BasicApp):
    def gengui(self):
        self.window=gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
    def destroy(self,widget,data=None):
        # delete_event returns False -> destroy
        gtk.main_quit()
    def delete_event(self,widget,event,data=None):
        # click "close" on title bar -> delete_event
        return False
if __name__=='__main__':
    app=TestApp()
    app.run()
