function getGroupId(currentid,kind) {
   var thisid=currentid;
   var row=Math.floor(thisid/9);
   var col=thisid%9;
   var idx,i,bi;
   var idlist=new Array();
   if (kind===1) {
       for(i=row*9;i<row*9+9;i++) {
           idlist.push(i);
       }
   } else if (kind===2) {
       for(i=col;i<81+col;i+=9) {
           idlist.push(i);
       }
   } else {
       for(bi=0;bi<9;bi++) {
           if(bi<3) {
               i=Math.floor(row/3)*3*9+Math.floor(col/3)*3+bi;
           } else if(bi<6) {
               i=Math.floor(row/3)*3*9+Math.floor(col/3)*3+bi+6;
           } else {
               i=Math.floor(row/3)*3*9+Math.floor(col/3)*3+bi+12;
           }
           idlist.push(i);
       }
   }
   return idlist;
}
function bitposition(intdata) {
	// get first bit position from bit0
	var tempdata,counter;
	tempdata=intdata+0;
	counter=0;
	while(tempdata>0) {
		counter++;
		if(tempdata%2>0) {
			break;
		}
		tempdata=tempdata>>1;
	}
	return counter;
}
function bitcount(intdata) {
	var tempdata,counter;
	tempdata=intdata+0;
	counter=0;
	while(tempdata>0) {
		if(tempdata%2>0) {
			counter++;
		}
		tempdata=tempdata>>1;
	}
	return counter;
}

function strikeout(workarea) {
	// strike out forbidden number
	var i,row,col,block,counter,cdata;
	for(i=0;i<workarea.length;i++) {
		if((workarea[i]&0x1000)>0) {
			cdata=bitposition(workarea[i]&0x01ff)-1;
			//Row
			row = getGroupId(i,1);
			for(counter=0;counter<row.length;counter++) {
				if((workarea[row[counter]]&0x1000)===0) {
					workarea[row[counter]]=workarea[row[counter]]&(~(1<<cdata));
				}
			}
			//Col
			col = getGroupId(i,2);
			for(counter=0;counter<col.length;counter++) {
				if((workarea[col[counter]]&0x1000)===0) {
					workarea[col[counter]]=workarea[col[counter]]&(~(1<<cdata));
				}
			}
			//Block
			block = getGroupId(i,3);
			for(counter=0;counter<block.length;counter++) {
				if((workarea[block[counter]]&0x1000)===0) {
					workarea[block[counter]]=workarea[block[counter]]&(~(1<<cdata));
				}
			}
		}
	}
}

function basicrule(workarea) {
	var bitrow=new Array(9);
	var bitcol=new Array(9);
	var bitblock=new Array(9);
	var recordrow=new Array(9);
	var recordcol=new Array(9);
	var recordblock=new Array(9);
	var i,j,row,col,block;
	// initialize flags
	for(i=0;i<9;i++) {
		bitrow[i]=[0,0,0,0,0,0,0,0,0];
		bitcol[i]=[0,0,0,0,0,0,0,0,0];
		bitblock[i]=[0,0,0,0,0,0,0,0,0];
		recordrow[i]=new Array(9);
		recordcol[i]=new Array(9);
		recordblock[i]=new Array(9);
	}
	// rule of 1~9
	for(i=0;i<workarea.length;i++) {
		row=Math.floor(i/9);
		col=i%9;
		block=Math.floor(row/3)*3+Math.floor(col/3);
		if((workarea[i]&0x1000)===0) {
			for(j=0;j<9;j++) {
				if((workarea[i]&(1<<j))>0) {
					bitrow[row][j]++;
					bitcol[col][j]++;
					bitblock[block][j]++;
					recordrow[row][j]=i;
					recordcol[col][j]=i;
					recordblock[block][j]=i;
				}
			}
		}
	}
	// update working array
	for(i=0;i<9;i++) {
		for(j=0;j<9;j++) {
			if(bitrow[i][j]===1) {
				workarea[recordrow[i][j]]=(1<<j);
			}
			if(bitcol[i][j]===1) {
				workarea[recordcol[i][j]]=(1<<j);
			}
			if(bitblock[i][j]===1) {
				workarea[recordblock[i][j]]=(1<<j);
			}
		}
	}
}

function pairs2(workarea) {
	var i;
	var row,col,block;
	for (i=0;i<9;i++) {
		row=getGroupId(i*9,1);
		col=getGroupId(i,2);
		block=getGroupId(i*12-Math.floor(i/3)*9,3);
		dopairs2(workarea,row);
		dopairs2(workarea,col);
		dopairs2(workarea,block);
	}
}

function dopairs2(workarea,idlist) {
	var j,k;
	var worktemp,workpair;
	worktemp=new Array();
	workpair=new Array();
	for (j=0;j<idlist.length;j++) {
		if((workarea[idlist[j]]&0x1000)===0) {
			if(bitcount(workarea[idlist[j]])===2) {
				k=worktemp.indexOf(workarea[idlist[j]]);
				if(k>=0) {
					workpair.push(workarea[idlist[j]]);
				} else {
					worktemp.push(workarea[idlist[j]]);
				}
			}
		}
	}
	if (workpair.length>0) {
		for (j=0;j<idlist.length;j++) {
			for(k=0;k<workpair.length;k++) {
				datamask=(~workpair[k]);
				if((workarea[idlist[j]]&0x1000)===0) {
					workarea[idlist[j]]=(workarea[idlist[j]] & datamask);
				}
			}
		}
	}
}

function countnew(workarea) {
	// count new data
	var i,counter;
	counter=0;
	for(i=0;i<workarea.length;i++) {
		if((workarea[i]&0x1000)===0) {
			if(bitcount(workarea[i])===1) {
				workarea[i]=workarea[i] | 0x1000;
				counter++;
			}
		}
	}
	return counter;
}

function makeworkarea(data,workarea) {
	var i;
	// initialize working array
	for(i=0;i<data.length;i++) {
		if(data[i]<1 || data[i]>9) {
			workarea[i]=0x01ff;
		} else {
			workarea[i]=(1<<(data[i]-1)) | 0x1000;
		}
	}
}

function updatebase(workarea,data) {
	var i;
	// set data array based on working array
	for(i=0;i<workarea.length;i++) {
		if((workarea[i]&0x1000)>0) {
			data[i]=bitposition(workarea[i]&0x01ff);
		}
	}
}

function solveonce(workarea) {
	// strike out forbidden number
	strikeout(workarea);

	// rule of 1~9
	basicrule(workarea);

	pairs2(workarea);
	// count new data
	return countnew(workarea);
}

function countunfinish(data) {
	var i,counter;
	counter=0;
	for(i=0;i<data.length;i++) {
		if(data[i]<1 || data[i]>9) {
			counter++;
		}
	}
	return counter;
}

function printdata(data) {
	for(var i=0;i<9;i++) {
		print(data.slice(i*9,i*9+9));
	}
}

function inputproblem(data) {
    data[0] =0;data[1] =9;data[2] =3; data[3] =7;data[4] =2;data[5] =0; data[6] =5;data[7] =6;data[8] =8;
    data[9] =2;data[10]=0;data[11]=8; data[12]=0;data[13]=6;data[14]=3; data[15]=9;data[16]=7;data[17]=1;
    data[18]=0;data[19]=6;data[20]=7; data[21]=0;data[22]=8;data[23]=9; data[24]=4;data[25]=3;data[26]=2;

    data[27]=3;data[28]=2;data[29]=4; data[30]=6;data[31]=1;data[32]=8; data[33]=7;data[34]=5;data[35]=9;
    data[36]=9;data[37]=7;data[38]=5; data[39]=3;data[40]=4;data[41]=2; data[42]=8;data[43]=1;data[44]=6;
    data[45]=6;data[46]=8;data[47]=1; data[48]=9;data[49]=7;data[50]=5; data[51]=2;data[52]=4;data[53]=3;

    data[54]=0;data[55]=0;data[56]=2; data[57]=0;data[58]=9;data[59]=6; data[60]=0;data[61]=8;data[62]=7;
    data[63]=8;data[64]=0;data[65]=6; data[66]=2;data[67]=5;data[68]=7; data[69]=0;data[70]=9;data[71]=4;
    data[72]=7;data[73]=0;data[74]=9; data[75]=8;data[76]=3;data[77]=0; data[78]=6;data[79]=2;data[80]=5;
}
function main() {
	var data=new Array(81);
	var workarea=new Array(81);
	var counter;

	// initialize base array
	inputproblem(data);
	// initialize working array
	makeworkarea(data,workarea);
	printdata(data);
	counter=solveonce(workarea);
	if(counter>0) {
		// set data array based on working array
		updatebase(workarea,data);
	}
	print(counter);
	while(counter>0) {
		printdata(data);
		counter=solveonce(workarea);
		if(counter>0) {
			// set data array based on working array
			updatebase(workarea,data);
		}
		print(counter);
		if(countunfinish(data)===0) {
			break;
		}
	}
	printdata(data);
}
//main();
