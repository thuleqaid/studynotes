import wx
import os
import re
import codecs
import IMix
import IUtils

class EncodePanel(IMix.IProgPanel):
	D_FILENAME_SUFFIX='.org'
	P_LANG_LIST=(re.compile(r'\.(c|c\+\+|cc|cp|cpp|cxx|h|h\+\+|hh|hp|hpp|hxx)$'),
				 re.compile(r'\.(py|pyx|pxd|pxi|scons)$'))
	D_ENCODE_LIST=('UTF8','CP932','CP936')
	D_LINEFEED_LIST=('DOS','UNIX','MAC')
	def __init__(self,parent):
		self.taskcount=0
		super(EncodePanel,self).__init__(parent,name='EncodePanel')
	def DoLayout(self):
		sizer1=wx.GridBagSizer()
		btn1=wx.Button(self,label='...')
		btn2=wx.Button(self,label='Change')
		btn3=wx.Button(self,label='Restore')
		self.srcpath=wx.TextCtrl(self)
		self.combo1=wx.ComboBox(self,value=self.__class__.D_ENCODE_LIST[0],choices=self.__class__.D_ENCODE_LIST,style=wx.CB_READONLY)
		self.combo2=wx.ComboBox(self,value=self.__class__.D_ENCODE_LIST[0],choices=self.__class__.D_ENCODE_LIST,style=wx.CB_READONLY)
		self.combo3=wx.ComboBox(self,value=self.__class__.D_LINEFEED_LIST[0],choices=self.__class__.D_LINEFEED_LIST,style=wx.CB_READONLY)
		self.listb=wx.ListBox(self,style=wx.LB_HSCROLL|wx.LB_NEEDED_SB)
		listfont=wx.Font(11,family=wx.FONTFAMILY_MODERN,style=wx.FONTSTYLE_NORMAL,weight=wx.FONTWEIGHT_NORMAL)
		self.listb.SetFont(listfont)
		sizer1.Add(wx.StaticText(self,label='SrcBase:'),(0,0),flag=wx.ALIGN_CENTER_VERTICAL)
		sizer1.Add(self.srcpath,(0,1),(1,6),flag=wx.ALIGN_CENTER_VERTICAL|wx.EXPAND)
		sizer1.Add(btn1,(0,7))
		sizer1.Add(self.combo1,(1,0))
		sizer1.Add(wx.StaticText(self,label='->'),(1,1),flag=wx.ALIGN_CENTER_VERTICAL)
		sizer1.Add(self.combo2,(1,2))
		sizer1.Add(self.combo3,(1,4))
		sizer1.Add(btn2,(1,6))
		sizer1.Add(btn3,(1,7))
		sizer1.Add(self.listb,(2,0),(1,8),flag=wx.EXPAND)
		sizer1.AddGrowableCol(5)
		sizer1.AddGrowableRow(2)
		self._sizer.Add(sizer1,1,flag=wx.EXPAND)
		self.Bind(wx.EVT_BUTTON,self.OnBtnChoose,btn1)
		self.Bind(wx.EVT_BUTTON,self.OnBtnChange,btn2)
		self.Bind(wx.EVT_BUTTON,self.OnBtnRestore,btn3)
	def OnBtnChoose(self,event):
		dd=wx.DirDialog(self,message='Select Source Folder')
		if wx.ID_OK==dd.ShowModal():
			srcpath=dd.GetPath()
			self.srcpath.ChangeValue(srcpath)
	def OnBtnChange(self,event):
		self.StartBusy()
		task=IMix.IWXThread((EncodePanel.walkdir,self,self.srcpath.GetValue(),self.combo1.GetStringSelection(),self.combo2.GetStringSelection(),self.combo3.GetStringSelection()),
							(EncodePanel.StopBusy,self))
		task.start()
	def OnBtnRestore(self,event):
		self.StartBusy()
		task=IMix.IWXThread((EncodePanel.restoredir,self,self.srcpath.GetValue()),(EncodePanel.StopBusy,self))
		task.start()
	def StartBusy(self):
		if self.taskcount<1:
			self.taskcount=1
		self.listb.Clear()
		super(EncodePanel,self).StartBusy()
	def StopBusy(self):
		self.taskcount-=1
		if self.taskcount<1:
			super(EncodePanel,self).StopBusy()
	def lineFeed(self,infile,outfile,format='UNIX'):
		CR='\r'
		LF='\n'
		CRLF=CR+LF
		fin=open(infile,'rU')
		data=fin.read()
		fin.close()
		if format.upper()=='DOS':
			data=re.sub(r'\n',CRLF,data)
		elif format.upper()=='MAC':
			data=re.sub(r'\n',CR,data)
		fout=open(outfile,'wb')
		fout.write(data)
		fout.close()
	def encode(self,infile,incode,outfile,outcode):
		fh=codecs.open(infile,'r',incode)
		data=fh.read()
		fh.close()
		fh=codecs.open(outfile,'w',outcode,errors='ignore')
		fh.write(data)
		fh.close()
	def AppendList(self,itemtext):
		self.listb.InsertItems((itemtext,),self.listb.GetCount())
	def walkdir(self,path,incode,outcode,format):
		pattern=self.__class__.P_LANG_LIST[0]
		for root,folders,files in os.walk(path):
			self.AppendList(root)
			for fname in files:
				if pattern.search(fname):
					fullpath=os.path.join(root,fname)
					bakpath=fullpath+self.__class__.D_FILENAME_SUFFIX
					os.rename(fullpath,bakpath)
					self.lineFeed(bakpath,fullpath,format)
					self.encode(fullpath,incode,fullpath,outcode)
	def restoredir(self,path):
		for root,folders,files in os.walk(path):
			self.AppendList(root)
			for fname in files:
				if fname.endswith(self.__class__.D_FILENAME_SUFFIX):
					fullpath=os.path.join(root,fname)
					bakpath=fullpath[:-4]
					if os.path.exists(bakpath):
						os.remove(bakpath)
					os.rename(fullpath,bakpath)
