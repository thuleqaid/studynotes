import wx
import math
from PIL import ImageGrab
from PIL import Image
import ImgConv
class SketchMagDialog(wx.Dialog):
    def __init__(self,parent,ID,magsize):
        wx.Dialog.__init__(self,parent,ID,style=wx.BORDER_SIMPLE|wx.STAY_ON_TOP)
        self.clientsize=magsize
        size=(magsize+1,magsize+1)
        self.SetClientSize(size)
        self.buffer=wx.EmptyBitmap(size[0],size[1])
        self.Bind(wx.EVT_PAINT,self.OnPaint)
    def ShowMag(self):
        self.Show(True)
    def Notify(self,buffer):
        dc=wx.BufferedDC(wx.ClientDC(self),self.buffer)
        dc.Clear()
        dc.DrawBitmap(buffer,0,0)
        dc.DrawLine(self.clientsize/2,0,self.clientsize/2,self.clientsize+1)
        dc.DrawLine(0,self.clientsize/2,self.clientsize+1,self.clientsize/2)
    def OnPaint(self,event):
        dc=wx.BufferedPaintDC(self,self.buffer)
        dc.DrawLine(self.clientsize/2,0,self.clientsize/2,self.clientsize+1)
        dc.DrawLine(0,self.clientsize/2,self.clientsize+1,self.clientsize/2)
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
            if event.ShiftDown():
                newPos=self.ModifyPoint(newPos)
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
            self.parent.SetStatusRight(self.CalcLength(self.curLine))
        else:
            self.parent.SetStatusRight(0)
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
            self.DrawCurLines(dc,self.curLine)
            self.parent.SetStatusRight(self.CalcLength(self.curLine))
        event.Skip()
    def OnMotion2(self,event):
        if self.pntcnt>0:
            newPos=event.GetPositionTuple()
            if event.ShiftDown():
                newPos=self.ModifyPoint(newPos)
            dc=self.ClearScreen()
            self.DrawLines(dc)
            templines=list(self.curLine)
            coords=self.pos+newPos
            templines.append(coords)
            self.DrawCurLines(dc,templines)
            self.parent.SetStatusRight(self.CalcLength(templines))
        event.Skip()
    def OnMotion(self,event):
        newPos=self.ClientToScreen(event.GetPosition())
        self.parent.NotifyMove((newPos.x,newPos.y))
        if self.lineMode==1:
            self.OnMotion1(event)
        elif self.lineMode==2:
            self.OnMotion2(event)
    def OnWheel(self,event):
        newPos=self.ClientToScreen(event.GetPosition())
        self.parent.NotifyWheel(event.GetWheelRotation(),(newPos.x,newPos.y))
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
    def DrawCurLines(self,dc,lines):
        dc.SetPen(self.pen)
        for coords in lines:
            dc.DrawLine(*coords)
    def ModifyPoint(self,newPos):
        if abs(newPos[0]-self.pos[0])>=(abs(newPos[1]-self.pos[1])*2):
            newPos2=(newPos[0],self.pos[1])
        elif (abs(newPos[0]-self.pos[0])*2)<=abs(newPos[1]-self.pos[1]):
            newPos2=(self.pos[0],newPos[1])
        else:
            deltax=newPos[0]-self.pos[0]
            deltay=newPos[1]-self.pos[1]
            delta=max(abs(deltax),abs(deltay))
            if deltax>0:
                deltax=delta
            else:
                deltax=-delta
            if deltay>0:
                deltay=delta
            else:
                deltay=-delta
            newPos2=(self.pos[0]+deltax,self.pos[1]+deltay)
        return newPos2
    def SetColor(self,color):
        #lineMode=1: unnecessary for checking drawing
        if self.lineMode==2 and self.pntcnt>0:
            return
        self.color=color
        self.pen=wx.Pen(self.color,self.thickness,wx.SOLID)
    def SetThickness(self,num):
        #lineMode=1: unnecessary for checking drawing
        if self.lineMode==2 and self.pntcnt>0:
            return
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
    def ToggleDrawMode(self,flag):
        if flag:
            self.lineMode=1
        else:
            self.lineMode=2
    def DrawUnitLine(self,screenx,screeny,unitlen):
        startpos=self.ScreenToClient((screenx,screeny))
        self.curLine=[(startpos.x,startpos.y+5,startpos.x+unitlen,startpos.y+5),]
        self.lines.append(("red",3,self.curLine))
        self.parent.SetStatusRight(self.CalcLength(self.curLine))
        self.curLine=[]
        self.pntcnt=0
        dc=self.ClearScreen()
        self.DrawLines(dc)

class SketchStatusBar(wx.StatusBar):
    def __init__(self,parent):
        wx.StatusBar.__init__(self,parent,-1)
        self.parent=parent
        self.SetFieldsCount(6)
        self.SetStatusWidths([-1,-2,-2,-2,-1,-1])
        self.sizeChanged=False
        self.Bind(wx.EVT_SIZE,self.OnSize)
        self.Bind(wx.EVT_IDLE,self.OnIdle)
        self.SetStatusText("Unit:",0)
        self.cb=wx.CheckBox(self,-1,"free hand")
        self.Bind(wx.EVT_CHECKBOX,self.OnToggleMode,self.cb)
        self.cb.SetValue(False)
        self.cp = wx.ColourPickerCtrl(self)
        self.Bind(wx.EVT_COLOURPICKER_CHANGED, self.OnPickColor, self.cp)
        self.slider=wx.Slider(self,-1,value=1,minValue=1,maxValue=10,style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS)
        self.Bind(wx.EVT_SCROLL_CHANGED,self.OnWidthChanged,self.slider)
        self.parent.ToggleMode(self.cb.GetValue())
        self.parent.SetColor(self.cp.GetColour().GetAsString(wx.C2S_CSS_SYNTAX))
        self.parent.SetThickness(self.slider.GetValue())
        self.btn=wx.Button(self,-1,"Clear",style=wx.NO_BORDER)
        self.Bind(wx.EVT_BUTTON,self.OnClear,self.btn)
        self.SetMinHeight(24)
        self.Reposition()
    def OnToggleMode(self,event):
        self.parent.ToggleMode(self.cb.GetValue())
        self.parent.sketch.SetFocus()
    def OnClear(self,event):
        self.parent.ClearScreen()
        self.parent.sketch.SetFocus()
    def OnPickColor(self,event):
        self.parent.SetColor(self.cp.GetColour().GetAsString(wx.C2S_CSS_SYNTAX))
        self.parent.sketch.SetFocus()
    def OnWidthChanged(self,event):
        self.parent.SetThickness(self.slider.GetValue())
        self.parent.sketch.SetFocus()
    def OnSize(self,event):
        self.Reposition()
        self.sizeChanged=True
    def OnIdle(self,event):
        if self.sizeChanged:
            self.Reposition()
    def SetStatusTextLeft(self,text):
        self.SetStatusText(text,0)
    def SetStatusTextRight(self,text):
        self.SetStatusText(text,5)
    def Reposition(self):
        rect=self.GetFieldRect(1)
        self.cb.SetPosition((rect.x+2,rect.y+2))
        self.cb.SetSize((rect.width-4,rect.height-4))
        rect=self.GetFieldRect(2)
        self.cp.SetPosition((rect.x+2,rect.y+2))
        self.cp.SetSize((rect.width-4,rect.height-4))
        rect=self.GetFieldRect(3)
        self.slider.SetPosition((rect.x+2,rect.y+2))
        self.slider.SetSize((rect.width-4,rect.height-4))
        rect=self.GetFieldRect(4)
        self.btn.SetPosition((rect.x+2,rect.y+2))
        self.btn.SetSize((rect.width-4,rect.height-4))
        self.sizeChanged=False

class SketchToolBar(wx.ToolBar):
    def __init__(self,parent):
        wx.ToolBar.__init__(self,parent)
        self.parent=parent
        self.btn2=wx.Button(self,-1,"Detect Unit")
        self.Bind(wx.EVT_BUTTON,self.OnDetectUnit,self.btn2)
        self.AddControl(self.btn2)
        self.btn=wx.Button(self,-1,"Unit")
        self.Bind(wx.EVT_BUTTON,self.OnUnit,self.btn)
        self.AddControl(self.btn)
        self.slider=wx.Slider(self,-1,value=200,minValue=32,maxValue=255,size=(200,-1),style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS)
        self.Bind(wx.EVT_SCROLL_CHANGED,self.OnTransparentChanged,self.slider)
        self.AddControl(self.slider)
        self.parent.SetTransparent(self.slider.GetValue())
        self.Realize()
    def OnDetectUnit(self,event):
        im=ImageGrab.grab()
        xsizea,ysizea=im.size
        lim=im.crop((0,ysizea/2,xsizea/2,ysizea)).convert("1").convert("L")
        xsize,ysize=lim.size
        minlen=10
        bflag=False
        for i in range(ysize):
            startpos=-1
            lastdata=-1
            cnt=0
            for j in range(xsize):
                data=lim.getpixel((j,ysize-i-1))
                if data==lastdata:
                    cnt+=1
                else:
                    if lastdata==0 and startpos<100 and cnt>minlen:
                        k=i
                        while ysize>k and lim.getpixel((startpos,ysize-k-1))==lastdata:
                            k+=1
                        if abs(k-i-cnt)<max(2,minlen/10):
                            bflag=True
                            ret=(startpos,ysizea-i-1,min(k-i,cnt))
                            break
                    startpos=j
                    lastdata=data
                    cnt=1
            if bflag:
                break
        if bflag:
            self.parent.sketch.DrawUnitLine(*ret)
            msgtext='Found unit line'
        else:
            msgtext='Cannot find unit line'
        msg=wx.MessageDialog(self,msgtext,'Detect Result')
        msg.ShowModal()
        self.parent.sketch.SetFocus()
    def OnUnit(self,event):
        self.parent.SetUnitLength()
        self.parent.sketch.SetFocus()
    def OnTransparentChanged(self,event):
        self.parent.SetTransparent(self.slider.GetValue())
        self.parent.sketch.SetFocus()

class MainFrame(wx.Frame):
    def __init__(self,parent=None,title="MainFrame"):
        wx.Frame.__init__(self,parent,-1,title,size=(640,480))
        self.sketch=SketchWindow(self,-1)
        self.unit=-1
        self.unit_m=-1
        self.lastlength=-1
        self.magsize=200
        self.magpos=0
        self.magdlg=SketchMagDialog(self,-1,self.magsize)
        self.mag=2
        self.lastxy=(0,0)
        self.InitToolBar()
        self.InitStatusBar()
        scr=wx.ScreenDC()
        scr.StartDrawingOnTop()
        self.scrsize=scr.GetSizeTuple()
        scr.EndDrawingOnTop()
        self.Maximize(True)
    def InitToolBar(self):
        self.tb=SketchToolBar(self)
        self.SetToolBar(self.tb)
    def InitStatusBar(self):
        self.sb=SketchStatusBar(self)
        self.SetStatusBar(self.sb)
    def ClearScreen(self):
        self.sketch.ClearScreen()
        self.sketch.ClearAll()
    def ToggleMode(self,flag):
        self.sketch.ToggleDrawMode(flag)
    def SetColor(self,color):
        self.sketch.SetColor(color)
    def SetThickness(self,width):
        self.sketch.SetThickness(width)
    def SetUnitLength(self):
        if self.lastlength>0:
            dlg=wx.TextEntryDialog(self, "Distance for a length of %.2f?"%(self.lastlength),"Please enter number")
            if self.unit_m>0:
                dlg.SetValue(str(self.unit_m))
            if dlg.ShowModal()==wx.ID_OK:
                value=dlg.GetValue()
                if value.isdigit():
                    self.unit_m=int(value)
                    self.unit=self.lastlength
                    text="%.2fP=%dM"%(self.unit,self.unit_m)
                    self.sb.SetStatusTextLeft(text)
    def SetStatusRight(self,length):
        self.lastlength=length
        if self.unit>0:
            text="%.2fM"%(length*self.unit_m/self.unit)
        else:
            text="%.2fP"%(length)
        self.sb.SetStatusTextRight(text)
    def NotifyWheel(self,rotate,xy):
        self.lastxy=xy
        if rotate>0 and self.mag<20:
            self.mag+=1
            if self.mag<4:
                self.magdlg.SetPosition((10,10))
                self.magpos=4
                self.magdlg.ShowMag()
                self.SetFocus()
            self.NotifyMove(self.lastxy)
        elif self.mag>2:
            self.mag-=1
            if self.mag<3:
                self.magdlg.Show(False)
            else:
                self.NotifyMove(self.lastxy)
    def NotifyMove(self,xy):
        if self.mag>2:
            self.RepositionMagDlg(xy)
            self.lastxy=xy
            radius=int(self.magsize/self.mag)
            rect=(xy[0]-radius,xy[1]-radius,xy[0]+radius,xy[1]+radius)
            buf=ImgConv.WxBitmapFromPilImage(ImageGrab.grab(rect).resize((self.magsize,self.magsize)))
            self.magdlg.Notify(buf)
    def RepositionMagDlg(self,xy):
        if xy[0]*3<self.scrsize[0]:
            if xy[1]*3<self.scrsize[1]:
                pos=1
                newpos=(self.scrsize[0]-self.magsize-10,self.scrsize[1]-self.magsize-10)
            elif xy[1]*3>self.scrsize[1]*2:
                pos=3
                newpos=(self.scrsize[0]-self.magsize-10,10)
            else:
                pos=self.magpos
        elif xy[0]*3>self.scrsize[0]*2:
            if xy[1]*2<self.scrsize[1]:
                pos=2
                newpos=(10,self.scrsize[1]-self.magsize-10)
            elif xy[1]*3>self.scrsize[1]*2:
                pos=4
                newpos=(10,10)
            else:
                pos=self.magpos
        else:
            pos=self.magpos
        if self.magpos!=pos:
            self.magpos=pos
            self.magdlg.SetPosition(newpos)

if __name__=='__main__':
    app=wx.App()
    frame=MainFrame()
    frame.Show(True)
    app.MainLoop()
