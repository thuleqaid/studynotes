import re;
import os;
import fnmatch;

def checkFile(filename):
	pat=re.compile(r'<\s*(a|link|img|script)\s+[^>]*\b(href|src)\s*=\s*"(?P<url>\S+?)(#\S+)*"')
	fh=open(filename,'rU')
	others=[]
	for m in pat.finditer(fh.read()):
		url=m.group('url')
		if (len(url)>0) and (url not in others):
			others.append(url)
	fh.close()
	return tuple(others)

def checkAll(path='.',rooturl='http://www.example.com',rootpath='root',baseurl='http://www.example.com/xxx/',htmlptn='*.html'):
	others=[]
	for root,dirs,files in os.walk(path):
		for f in files:
			if fnmatch.fnmatch(f,htmlptn):
				temp=checkFile(os.path.join(root,f))
				for item in temp:
					if item not in others:
						others.append(item)
	temp=[]
	for item in others:
		if item.startswith('http:'):
			pass
		elif item.startswith('https:'):
			pass
		elif item.startswith('ftp:'):
			pass
		elif item.startswith('#'):
			pass
		elif item.find('@')>=0:
			pass
		else:
			if item.startswith('/'):
				item2=rootpath+item
			else:
				item2=item
			if not os.path.exists(item2):
				temp.append(item)
	temp.sort()
	for item in temp:
		if item.find('.')>=0:
			if item.startswith('/'):
				if item.endswith('/'):
					print("#curl --create-dirs %s%s -o %s%s" % (rooturl,item,rootpath,item))
				else:
					print("curl --create-dirs %s%s -o %s%s" % (rooturl,item,rootpath,item))
			else:
				if item.endswith('/'):
					print("#curl --create-dirs %s%s -o %s" % (baseurl,item,item))
				else:
					print("curl --create-dirs %s%s -o %s" % (baseurl,item,item))

if __name__=='__main__':
	rooturl=r'http://devoloper.gnome.org'
	baseurl=r'http://developer.gnome.org/pygtk/stable/'
	rootpath=r'root'
	checkAll('.',rooturl,rootpath,baseurl,'*.html')
