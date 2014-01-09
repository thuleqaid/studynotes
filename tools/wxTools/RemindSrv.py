# -*- coding:utf-8 -*-
import wx
from twisted.internet import protocol
from time import sleep
import threading
import ConfigParser

class MsgDialogThread(threading.Thread):
	def __init__(self,msg,interval=()):
		super(self.__class__,self).__init__()
		self.msg=msg
		self.interval=tuple(int(x) for x in interval)
	def sec2text(self,sec):
		label=''
		timem=sec/60
		times=sec%60
		if timem==0:
			label=u'%d秒後'%(times,)
		else:
			if times==0:
				label=u'%d分後'%(timem,)
			else:
				label=u'%d分後%d秒後'%(timem,times)
		return label
	def run(self):
		ilen=len(self.interval)
		if ilen==0:
			style=wx.OK
			label=((u'完成'),(''),(''))
		elif ilen==1:
			style=wx.YES_NO
			label=((u'完成'),(self.sec2text(self.interval[0])),(''))
		else:
			style=wx.YES_NO|wx.CANCEL
			label=((u'完成'),(self.sec2text(self.interval[0])),(self.sec2text(self.interval[1])))
		msgbox=wx.MessageDialog(parent=None,
							 message=self.msg,
							 caption='Remind',
							 style=style|wx.STAY_ON_TOP)
		msgbox.SetYesNoCancelLabels(*label)
		msgbox.SetOKLabel(label[0])
		ret=msgbox.ShowModal()
		while ret not in (wx.ID_YES,wx.ID_OK):
			if ret==wx.ID_NO:
				stime=self.interval[0]
			elif ret==wx.ID_CANCEL:
				stime=self.interval[1]
			else:
				stime=60
			sleep(stime)
			ret=msgbox.ShowModal()
class RemindServer(protocol.Protocol):
	def __init__(self,conffile):
		config=ConfigParser.ConfigParser()
		config.read(conffile)
		if config.has_option('Remind','Count'):
			count=min(2,config.getint('Remind','Count'))
		else:
			count=0
		data=[]
		if count>0:
			for i in range(count):
				item='Interval%d'%(i+1,)
				data.append(config.getint('Remind',item))
		self.interval=tuple(data)
	def dataReceived(self,data):
		MsgDialogThread(data,self.interval).start()
class RemindServerFactory(protocol.Factory):
	def __init__(self,conffile):
		self.conffile=conffile
	def buildProtocol(self,addr):
		return RemindServer(self.conffile)

def startRemindSrv(reactor,conffile):
	reactor.listenTCP(9999,RemindServerFactory(conffile))
