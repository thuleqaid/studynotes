import wx
import math

class SketchWindow(wx.Window):
    def __init__(self,parent,ID):
        wx.Window.__init__(self,parent,ID)
        self.parent=parent
        self.SetBackgroundColour("White")
        self.color="Black"
        self.thickness=1
        self.pen=wx.Pen(self.color,self.thickness,wx.SOLID)
        # lineMode: 1 for drag mode, 2 for click mode
        self.lineMode=2
        self.lines=[]
        self.curLine=[]
        self.pos=(0,0)
        self.pntcnt=0
        self.InitBuffer()
        self.Bind(wx.EVT_LEFT_DOWN,self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP,self.OnLeftUp)
        self.Bind(wx.EVT_RIGHT_DOWN,self.OnRightDown)
        self.Bind(wx.EVT_MOTION,self.OnMotion)
        self.Bind(wx.EVT_MOUSEWHEEL,self.OnWheel)
        self.Bind(wx.EVT_SIZE,self.OnSize)
        self.Bind(wx.EVT_IDLE,self.OnIdle)
        self.Bind(wx.EVT_PAINT,self.OnPaint)
    def InitBuffer(self):
        size=self.GetClientSize()
        self.buffer=wx.EmptyBitmap(size.width,size.height)
        dc=wx.BufferedDC(None,self.buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        self.DrawLines(dc)
        self.reInitBuffer=False
    def OnLeftDown1(self,event):
        self.curLine=[]
        self.pos=event.GetPositionTuple()
        self.CaptureMouse()
    def OnLeftDown2(self,event):
        newPos=event.GetPositionTuple()
        if self.pntcnt<1:
            pass
        elif self.pntcnt>0:
            coords=self.pos+newPos
            self.curLine.append(coords)
        self.pntcnt+=1
        self.pos=newPos
    def OnLeftDown(self,event):
        if self.lineMode==1:
            self.OnLeftDown1(event)
        elif self.lineMode==2:
            self.OnLeftDown2(event)
    def OnLeftUp1(self,event):
        if self.HasCapture():
            self.lines.append((self.color,self.thickness,self.curLine))
            self.curLine=[]
            self.ReleaseMouse()
    def OnLeftUp2(self,event):
        pass
    def OnLeftUp(self,event):
        if self.lineMode==1:
            self.OnLeftUp1(event)
        elif self.lineMode==2:
            self.OnLeftUp2(event)
    def OnRightDown1(self,event):
        pass
    def OnRightDown2(self,event):
        if self.pntcnt>1:
            self.lines.append((self.color,self.thickness,self.curLine))
        self.curLine=[]
        self.pntcnt=0
        dc=self.ClearScreen()
        self.DrawLines(dc)
    def OnRightDown(self,event):
        if self.lineMode==1:
            self.OnRightDown1(event)
        elif self.lineMode==2:
            self.OnRightDown2(event)
    def OnMotion1(self,event):
        if event.Dragging() and event.LeftIsDown():
            newPos=event.GetPositionTuple()
            coords=self.pos+newPos
            self.curLine.append(coords)
            self.pos=newPos
            dc=self.ClearScreen()
            self.DrawLines(dc)
            self.DrawCurLines(dc)
        event.Skip()
    def OnMotion2(self,event):
        if self.pntcnt>0:
            dc=self.ClearScreen()
            self.DrawLines(dc)
            self.DrawCurLines(dc)
            newPos=event.GetPositionTuple()
            coords=self.pos+newPos
            dc.DrawLine(*coords)
        event.Skip()
    def OnMotion(self,event):
        if self.lineMode==1:
            self.OnMotion1(event)
        elif self.lineMode==2:
            self.OnMotion2(event)
    def OnWheel(self,event):
        if self.lineMode==1:
            if not event.LeftIsDown():
                self.lineMode=2
        elif self.lineMode==2:
            if self.pntcnt<1:
                self.lineMode=1
    def OnSize(self,event):
        self.reInitBuffer=True
    def OnIdle(self,event):
        if self.reInitBuffer:
            self.InitBuffer()
            self.Refresh(False)
    def OnPaint(self,event):
        dc=wx.BufferedPaintDC(self,self.buffer)
    def DrawLines(self,dc):
        for color,thickness,line in self.lines:
            pen=wx.Pen(color,thickness,wx.SOLID)
            dc.SetPen(pen)
            for coords in line:
                dc.DrawLine(*coords)
    def DrawCurLines(self,dc):
        dc.SetPen(self.pen)
        for coords in self.curLine:
            dc.DrawLine(*coords)
    def SetColor(self,color):
        self.color=color
        self.pen=wx.Pen(self.color,self.thickness,wx.SOLID)
    def SetThickness(self,num):
        self.thickness=num
        self.pen=wx.Pen(self.color,self.thickness,wx.SOLID)
    def ClearScreen(self):
        dc=wx.BufferedDC(wx.ClientDC(self),self.buffer)
        dc.Clear()
        return dc
    def ClearAll(self):
        self.ClearScreen()
        self.lines=[]
        self.curLine=[]
        self.pos=(0,0)
        self.pntcnt=0
    def CalcLength(self,lines):
        length=0.0
        for line in lines:
            length+=math.sqrt((line[0]-line[2])*(line[0]-line[2])+(line[1]-line[3])*(line[1]-line[3]))
        return length

class MainFrame(wx.Frame):
    def __init__(self,parent=None,title="MainFrame"):
        wx.Frame.__init__(self,parent,-1,title,size=(400,200))
        self.sketch=SketchWindow(self,-1)

if __name__=='__main__':
    app=wx.PySimpleApp()
    frame=MainFrame()
    frame.Show(True)
    app.MainLoop()
