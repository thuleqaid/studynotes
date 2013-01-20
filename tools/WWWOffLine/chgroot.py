import re;
import os;
import fnmatch;

def checkFile(filename):
	pat=re.compile(r'<\s*(a|link|img|script)\s+[^>]*\b(href|src)\s*=\s*"/(?P<url>\S+?)(#\S+)*"')
	fh=open(filename,'rU')
	flag=False
	for m in pat.finditer(fh.read()):
		url=m.group('url')
		if (url.find('.')>0) and (not url.endswith('/')):
			flag=True
			break
	fh.close()
	return flag
def modifyFile(filename,rootpath):
	pat=re.compile(r'<\s*(?:a|link|img|script)\s+[^>]*\b(?:href|src)\s*=\s*"(?P<url>/\S+?)(?:#\S+)*"')
	bakfile=filename+'.bak'
	os.rename(filename,bakfile)
	fin=open(bakfile,'rU')
	lastend=0
	intext=fin.read()
	out=''
	fin.close()
	for m in pat.finditer(intext):
		url=m.group('url')
		if (url.find('.')>0) and (not url.endswith('/')):
			out+=intext[lastend:m.start('url')]+rootpath+intext[m.start('url'):m.end(0)]
			lastend=m.end(0)
	fout=open(filename,'wb')
	fout.write(out)
	fout.close()

def checkAll(path='.',rootpath='root',htmlptn='*.html'):
	others=[]
	for root,dirs,files in os.walk(path):
		for f in files:
			if fnmatch.fnmatch(f,htmlptn):
				filepath=os.path.join(root,f)
				temp=checkFile(filepath)
				if temp:
					others.append(filepath)
	for f in others:
		modifyFile(f,rootpath)

if __name__=='__main__':
	rootpath=r'root'
	checkAll('.',rootpath,'*.html')
