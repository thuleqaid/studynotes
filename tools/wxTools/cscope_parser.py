import os
import re
import pickle
import sys
import nodemap
class CscopeParser:
	Flag_body=1
	Flag_called=2
	Pat_file=re.compile(r'^\t@(?P<file>.+)$')
	Pat_line=re.compile(r'^(?P<line>\d+)')
	Pat_funcbody=re.compile(r'^\t\$(?P<func>.+)$')
	Pat_funccalled=re.compile(r'^\t`(?P<func>.+)$')
	Cache_file=u'cscope.cache'
	def __init__(self,dbfile=u'cscope.out',verbose=False,cache=False):
		self._dbpath=''
		self._dbfile=''
		self._cachefile=CscopeParser.Cache_file
		self._verbose=verbose
		self._cacheflag=cache
		self.outlog(u'Create CscopeParser')
		self.SetDBFile(dbfile)
		#self._data=[(file_index,lineno,func_index,body/called,outer_func_index),...]
		self._data=[]
		self._files=[]
		self._funcs=[]
		#self._matrix={funcno:{func_out_index:[count,[data_index,...]],...},...}
		self._matrix={}
		self._trackfunc=-1
	def SetDBFile(self,dbfile):
		if (os.path.exists(dbfile) and os.path.isfile(dbfile)):
			(self._dbpath,self._dbfile)=os.path.split(dbfile)
			if self._dbpath:
				self.outlog(u'Chdir to '+self._dbpath)
				os.chdir(self._dbpath)
			self._parseflag=False
			self.outlog(u'Set Cscope DB file: '+self._dbfile)
	def SetVerbose(self,verbose):
		self._verbose=verbose
	def outlog(self,outtext,newline=True):
		if self._verbose:
			if newline:
				print outtext
			else:
				print outtext,
	def _existcache(self):
		if os.path.exists(self._cachefile) and os.path.getmtime(self._cachefile)>os.path.getmtime(self._dbfile):
			return True
		else:
			return False
	def DoParse(self):
		self.outlog(u'Starting parse DB: '+self._dbfile)
		self._data=[]
		self._files=[]
		self._funcs=[]
		if self._cacheflag and self._existcache():
			with open(self._cachefile,'r') as cache:
				(self._files,self._funcs,self._data)=pickle.load(cache)
		else:
			with open(self._dbfile,'r') as db:
				db_file=''
				db_line=''
				db_func=''
				db_func2=''
				linecount=0
				for line in db:
					linecount+=1
					if linecount%2500==0:
						processcount=linecount/2500
						processcount=processcount%4
						if processcount==0:
							self.outlog(u'|',False)
						elif processcount==1:
							self.outlog(u'/',False)
						elif processcount==2:
							self.outlog(u'-',False)
						elif processcount==3:
							self.outlog(u'\\',False)
					ret1=CscopeParser.Pat_file.search(line)
					ret2=CscopeParser.Pat_line.search(line)
					ret3=CscopeParser.Pat_funcbody.search(line)
					ret4=CscopeParser.Pat_funccalled.search(line)
					if ret1:
						db_file=ret1.group('file')
						if db_file not in self._files:
							self._files.append(db_file)
						db_fileno=self._files.index(db_file)
						db_func=''
					elif db_file:
						if ret2:
							db_line=int(ret2.group('line'))
						elif ret3:
							db_func=ret3.group('func')
							if db_func not in self._funcs:
								self._funcs.append(db_func)
							db_funcno=self._funcs.index(db_func)
							self._data.append((db_fileno,db_line,db_funcno,CscopeParser.Flag_body,))
						elif ret4:
							if db_func:
								db_func2=ret4.group('func')
								if db_func2 not in self._funcs:
									self._funcs.append(db_func2)
								db_funcno2=self._funcs.index(db_func2)
								self._data.append((db_fileno,db_line,db_funcno2,CscopeParser.Flag_called,db_funcno,))
				self.outlog(u'')
			if self._cacheflag:
				with open(self._cachefile,'w') as cache:
					pickle.dump((self._files,self._funcs,self._data),cache)
		self._parseflag=True
		self.outlog(u'... Parse Over.')
	def _trackone(self,funcno,checkindex,outindex):
		#matrix={func_out_index:[count,[data_index,...]],...}
		matrix={}
		for index,item in enumerate(self._data):
			if (item[3]==CscopeParser.Flag_called and item[checkindex]==funcno):
				if item[outindex] not in matrix:
					matrix[item[outindex]]=[0,[],]
				matrix[item[outindex]][0]+=1
				matrix[item[outindex]][1].append(index)
		return matrix
	def _trackall(self,funcno,checkindex,outindex):
		checklist=[funcno,]
		self._matrix={}
		self._trackfunc=funcno
		while len(checklist)>0:
			nextlist=[]
			for item in checklist:
				self._matrix[item]=self._trackone(item,checkindex,outindex)
				for nextitem in self._matrix[item].iterkeys():
					if ((nextitem not in self._matrix) and (nextitem not in nextlist)):
						nextlist.append(nextitem)
			checklist[:]=nextlist[:]
	def DoTrack(self,funcname,direction):
		if self._parseflag:
			if funcname in self._funcs:
				self.outlog(u'Start track '+unicode(funcname)+u':')
				funcno=self._funcs.index(funcname)
				if direction==CscopeParser.Flag_called:
					self._trackall(funcno,2,4)
				else:
					self._trackall(funcno,4,2)
				self.outlog(u'...Track Over.')
	def _report1(self,dir):
		checklist=[self._trackfunc,]
		outs={}
		used=[]
		while len(checklist)>0:
			nextlist=[]
			for item in checklist:
				used.append(item)
				for nextitem in self._matrix[item].iterkeys():
					if dir==CscopeParser.Flag_body:
						outtxt=self._funcs[item]+u','+self._funcs[nextitem]
					else:
						outtxt=self._funcs[nextitem]+u','+self._funcs[item]
					if outtxt in outs:
						if outs[outtxt]<self._matrix[item][nextitem][0]:
							outs[outtxt]=self._matrix[item][nextitem][0]
					else:
						outs[outtxt]=self._matrix[item][nextitem][0]
					if ((nextitem not in used) and (nextitem not in nextlist)):
						nextlist.append(nextitem)
			checklist[:]=nextlist[:]
		return outs
	def _merge1(self,args):
		outs={}
		for item in args:
			for key,value in item.items():
				if key in outs:
					outs[key]=max(outs[key],value)
				else:
					outs[key]=value
		return outs
	def _output1(self,filename,arg,allowrepeat=True,**kwargs):
		with open(filename,'w') as f:
			f.write(u"digraph G {\n")
			color=kwargs.get('color',None)
			funcs=kwargs.get('funcs',None)
			if color and funcs:
				for func in funcs:
					f.write(u"\t%s [color=%s];\n"%(func,color))
			for key in sorted(arg.iterkeys()):
				if allowrepeat:
					value=arg[key]
				else:
					value=1
				for i in range(value):
					f.write(u"\t"+key.replace(u',',u' -> ')+u";\n")
			f.write(u"}\n")

	def Report(self,fmt,dir):
		if len(self._matrix)>0:
			if fmt=='dot':
				return self._report1(dir)
		return None
	def Merge(self,fmt,args):
		if len(args)>1:
			if fmt=='dot':
				return self._merge1(args)
		return None
	def Output(self,fmt,filename,arg,allowrepeat=True,**kwargs):
		filename=filename+u'.'+fmt
		if fmt=='dot':
			self._output1(filename,arg,allowrepeat,**kwargs)
	def TrackUp(self,funcs,fmt='dot',allowrepeat_func=True,allowrepeat_all=False):
		outs=[]
		for func in funcs:
			self.DoTrack(func,CscopeParser.Flag_called)
			outs.append(self.Report(fmt,CscopeParser.Flag_called))
			self.Output(fmt,func+u'#d',outs[-1],allowrepeat_func)
		if len(funcs)>1:
			out=self.Merge(fmt,outs)
			self.Output(fmt,u'_ALL_#d',out,allowrepeat_all,color='red',funcs=funcs)
	def TrackDown(self,funcs,fmt='dot',allowrepeat_func=True,allowrepeat_all=False,maxlevel=0,exfuncs=()):
		outs=[]
		for func in funcs:
			self.DoTrack(func,CscopeParser.Flag_body)
			outs.append(self.Report(fmt,CscopeParser.Flag_body))
			filtered=self._restrict(outs[-1],maxlevel,exfuncs)
			self.Output(fmt,func+u'#c',filtered,allowrepeat_func)
		if len(funcs)>1:
			out=self.Merge(fmt,outs)
			filtered=self._restrict(out,maxlevel,exfuncs)
			self.Output(fmt,u'_ALL_#c',filtered,allowrepeat_all,color='red',funcs=funcs)
	def _restrict(self,dotcontent,maxlvl,exfuncs):
		if maxlvl<=0 and len(exfuncs)<=0:
			return dotcontent
		nm=nodemap.NodeMap()
		for k in dotcontent.keys():
			nodes=k.split(',')
			nm.addEdge(nodes[0],nodes[1],1)
		markhash=nm.getMarkHash()
		mhead=nm.getMapHead()
		nlist=nm.getNodeList()
		rmlist=[]
		if maxlvl>0:
			for node in nlist:
				dist=sys.maxint
				for head in mhead:
					dist=min(markhash[node][head],dist)
				if dist>maxlvl:
					rmlist.append(node)
		if len(exfuncs)>0:
			for exf in exfuncs:
				if exf not in rmlist:
					rmlist.append(exf)
		nm.deleteNode(*rmlist)
		outdict={}
		for edge in nm.getEdges():
			k="{snode},{enode}".format(**edge)
			outdict[k]=dotcontent[k]
		return outdict

if __name__ == '__main__':
	cp=CscopeParser(verbose=True,cache=True)
	cp.DoParse()
	func='plotrequest'
	cp.TrackUp(func)
