var info;
function init () {
	_initInfo();
	_initPath();
	top.register('info',msg_info);
	top.register('setcolor',setColorByTitle);
	$("text").click(function test(event) {
		var t=event.target;
		alert(t.textContent);
	});
}
function _getNodeId(title) {
	id='';
	for (i=0;i<info['nodes'].length;++i) {
		if (info['nodes'][i]['title'] == title) {
			id=info['nodes'][i]['id'];
			break;
		}
	}
	return id;
}
function _initInfo () {
	var classname="";
	var itemid="";
	var itemtext="";
	var blocksrc;
	var edgepattern=/(.+)->(.+)/;
	var root=document.getElementById("graph1");
	var x=root.firstChild;
	info=[];
	info['nodes']=[];
	info['edges']=[];
	do {
		if (x.nodeName == 'g') {
			blocksrc=[];
			classname=x.getAttributeNS(null,"class");
			itemid=x.getAttributeNS(null,"id");
			y=x.firstChild;
			do {
				if (y.nodeName == 'title') {
					itemtext=y.textContent;
				} else if (y.nodeName == 'text') {
					blocksrc[blocksrc.length]=y.textContent;
				}
			} while(y=y.nextSibling);
			if(classname=="node") {
				info['nodes'][info['nodes'].length]={'id':itemid,'title':itemtext,'src':blocksrc};
			} else if(classname=="edge") {
				result=itemtext.match(edgepattern);
				if (result!=null) {
					info['edges'][info['edges'].length]={'id':itemid,'from':result[1],'to':result[2]};
				}
			}
		}
	} while(x=x.nextSibling);
}
function _initPath() {
	var edgematrix=[];
	var i=0,from='',to='';
	for (i=0;i<info['edges'].length;++i) {
		from=info['edges'][i]['from'];
		to=info['edges'][i]['to'];
		if (edgematrix.indexOf(from)<0) {
			edgematrix[from]=[];
		}
		edgematrix[from][to]=1;
	}
}
function msg_info() {
	var i=0,j=0;
	var outtext='';
	for (i=0;i<info['nodes'].length;++i) {
		outtext='';
		for (j in info['nodes'][i]) outtext+=j+":"+info['nodes'][i][j]+"\n";
		alert(outtext);
	}
	for (i=0;i<info['edges'].length;++i) {
		outtext='';
		for (j in info['edges'][i]) outtext+=j+":"+info['edges'][i][j]+"\n";
		alert(outtext);
	}
}
function setColorByTitle(color,titlelist) {
	for (var i=0;i<titlelist.length;++i) {
		nodeid=_getNodeId(titlelist[i]);
		if (nodeid!='') {
			node=document.getElementById(nodeid);
			node.setAttributeNS(null,"fill",color);
		}
	}
}