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
	data[0]=0;
	data[1]=0;
	data[2]=3;
	data[3]=0;
	data[4]=9;
	data[5]=4;
	data[6]=0;
	data[7]=8;
	data[8]=2;

	data[9] =0;
	data[10]=0;
	data[11]=5;
	data[12]=1;
	data[13]=7;
	data[14]=2;
	data[15]=0;
	data[16]=3;
	data[17]=0;

	data[18]=0;
	data[19]=9;
	data[20]=2;
	data[21]=0;
	data[22]=0;
	data[23]=6;
	data[24]=1;
	data[25]=0;
	data[26]=5;

	data[27]=0;
	data[28]=5;
	data[29]=0;
	data[30]=0;
	data[31]=0;
	data[32]=1;
	data[33]=9;
	data[34]=0;
	data[35]=8;

	data[36]=0;
	data[37]=8;
	data[38]=6;
	data[39]=0;
	data[40]=2;
	data[41]=0;
	data[42]=7;
	data[43]=5;
	data[44]=0;

	data[45]=3;
	data[46]=0;
	data[47]=9;
	data[48]=7;
	data[49]=0;
	data[50]=0;
	data[51]=0;
	data[52]=6;
	data[53]=0;

	data[54]=9;
	data[55]=0;
	data[56]=8;
	data[57]=2;
	data[58]=0;
	data[59]=0;
	data[60]=3;
	data[61]=1;
	data[62]=0;

	data[63]=0;
	data[64]=2;
	data[65]=0;
	data[66]=8;
	data[67]=1;
	data[68]=3;
	data[69]=5;
	data[70]=0;
	data[71]=0;

	data[72]=5;
	data[73]=3;
	data[74]=0;
	data[75]=9;
	data[76]=6;
	data[77]=0;
	data[78]=0;
	data[79]=0;
	data[80]=0;
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
