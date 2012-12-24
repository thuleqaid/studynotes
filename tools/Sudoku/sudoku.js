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
	var i,row,col,brow,bcol,counter,cdata;
	for(i=0;i<workarea.length;i++) {
		row=Math.floor(i/9);
		col=i%9;
		brow=Math.floor(row/3);
		bcol=Math.floor(col/3);
		if((workarea[i]&0x1000)>0) {
			cdata=bitposition(workarea[i]&0x01ff)-1;
			//Row
			for(counter=row*9;counter<row*9+9;counter++) {
				if((workarea[counter]&0x1000)===0) {
					workarea[counter]=workarea[counter]&(~(1<<cdata));
				}
			}
			//Col
			for(counter=col;counter<81+col;counter+=9) {
				if((workarea[counter]&0x1000)===0) {
					workarea[counter]=workarea[counter]&(~(1<<cdata));
				}
			}
			//Block
			for(counter=brow*3*9+bcol*3;counter<brow*3*9+bcol*3+27;counter+=9) {
				if((workarea[counter]&0x1000)===0) {
					workarea[counter]=workarea[counter]&(~(1<<cdata));
				}
				if((workarea[counter+1]&0x1000)===0) {
					workarea[counter+1]=workarea[counter+1]&(~(1<<cdata));
				}
				if((workarea[counter+2]&0x1000)===0) {
					workarea[counter+2]=workarea[counter+2]&(~(1<<cdata));
				}
			}
		}
	}
}

function basicrule(workarea) {
	var bittest=new Array(9);
	var bitrecord=new Array(9);
	var i,row,col,brow,bcol;
	// rule of 1~9
	// Row
	for(row=0;row<9;row++) {
		bittest[0]=0;
		bittest[1]=0;
		bittest[2]=0;
		bittest[3]=0;
		bittest[4]=0;
		bittest[5]=0;
		bittest[6]=0;
		bittest[7]=0;
		bittest[8]=0;
		for(col=0;col<9;col++) {
			i=row*9+col;
			if((workarea[i]&0x1000)===0) {
				if((workarea[i]&0x0001)>0) {
					bittest[0]++;
					bitrecord[0]=i;
				}
				if((workarea[i]&0x0002)>0) {
					bittest[1]++;
					bitrecord[1]=i;
				}
				if((workarea[i]&0x0004)>0) {
					bittest[2]++;
					bitrecord[2]=i;
				}
				if((workarea[i]&0x0008)>0) {
					bittest[3]++;
					bitrecord[3]=i;
				}
				if((workarea[i]&0x0010)>0) {
					bittest[4]++;
					bitrecord[4]=i;
				}
				if((workarea[i]&0x0020)>0) {
					bittest[5]++;
					bitrecord[5]=i;
				}
				if((workarea[i]&0x0040)>0) {
					bittest[6]++;
					bitrecord[6]=i;
				}
				if((workarea[i]&0x0080)>0) {
					bittest[7]++;
					bitrecord[7]=i;
				}
				if((workarea[i]&0x0100)>0) {
					bittest[8]++;
					bitrecord[8]=i;
				}
			}
		}
		for(col=0;col<9;col++) {
			if(bittest[col]===1) {
				workarea[bitrecord[col]]=(1<<col);
			}
		}
	}
	// Col
	for(col=0;col<9;col++) {
		bittest[0]=0;
		bittest[1]=0;
		bittest[2]=0;
		bittest[3]=0;
		bittest[4]=0;
		bittest[5]=0;
		bittest[6]=0;
		bittest[7]=0;
		bittest[8]=0;
		for(row=0;row<9;row++) {
			i=row*9+col;
			if((workarea[i]&0x1000)===0) {
				if((workarea[i]&0x0001)>0) {
					bittest[0]++;
					bitrecord[0]=i;
				}
				if((workarea[i]&0x0002)>0) {
					bittest[1]++;
					bitrecord[1]=i;
				}
				if((workarea[i]&0x0004)>0) {
					bittest[2]++;
					bitrecord[2]=i;
				}
				if((workarea[i]&0x0008)>0) {
					bittest[3]++;
					bitrecord[3]=i;
				}
				if((workarea[i]&0x0010)>0) {
					bittest[4]++;
					bitrecord[4]=i;
				}
				if((workarea[i]&0x0020)>0) {
					bittest[5]++;
					bitrecord[5]=i;
				}
				if((workarea[i]&0x0040)>0) {
					bittest[6]++;
					bitrecord[6]=i;
				}
				if((workarea[i]&0x0080)>0) {
					bittest[7]++;
					bitrecord[7]=i;
				}
				if((workarea[i]&0x0100)>0) {
					bittest[8]++;
					bitrecord[8]=i;
				}
			}
		}
		for(row=0;row<9;row++) {
			if(bittest[row]===1) {
				workarea[bitrecord[row]]=(1<<row);
			}
		}
	}
	// Block
	for(brow=0;brow<3;brow++) {
		for(bcol=0;bcol<3;bcol++) {
			bittest[0]=0;
			bittest[1]=0;
			bittest[2]=0;
			bittest[3]=0;
			bittest[4]=0;
			bittest[5]=0;
			bittest[6]=0;
			bittest[7]=0;
			bittest[8]=0;
			for(row=brow*3;row<brow*3+3;row++) {
				for(col=bcol*3;col<bcol*3+3;col++) {
					i=row*9+col;
					if((workarea[i]&0x1000)===0) {
						if((workarea[i]&0x0001)>0) {
							bittest[0]++;
							bitrecord[0]=i;
						}
						if((workarea[i]&0x0002)>0) {
							bittest[1]++;
							bitrecord[1]=i;
						}
						if((workarea[i]&0x0004)>0) {
							bittest[2]++;
							bitrecord[2]=i;
						}
						if((workarea[i]&0x0008)>0) {
							bittest[3]++;
							bitrecord[3]=i;
						}
						if((workarea[i]&0x0010)>0) {
							bittest[4]++;
							bitrecord[4]=i;
						}
						if((workarea[i]&0x0020)>0) {
							bittest[5]++;
							bitrecord[5]=i;
						}
						if((workarea[i]&0x0040)>0) {
							bittest[6]++;
							bitrecord[6]=i;
						}
						if((workarea[i]&0x0080)>0) {
							bittest[7]++;
							bitrecord[7]=i;
						}
						if((workarea[i]&0x0100)>0) {
							bittest[8]++;
							bitrecord[8]=i;
						}
					}
				}
			}
			for(row=0;row<9;row++) {
				if(bittest[row]===1) {
					workarea[bitrecord[row]]=(1<<row);
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

function solveonce(data) {
	var workarea=new Array(81);
	var counter;

	// initialize working array
	makeworkarea(data,workarea);

	// strike out forbidden number
	strikeout(workarea);

	// rule of 1~9
	basicrule(workarea);

	// count new data
	counter=countnew(workarea);

	if(counter>0) {
		// set data array based on working array
		updatebase(workarea,data);
	}
	return counter;
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
	var counter;
	inputproblem(data);
	printdata(data);
	counter=solveonce(data);
	print(counter);
	while(counter>0) {
		printdata(data);
		counter=solveonce(data);
		print(counter);
		if(countunfinish(data)===0) {
			break;
		}
	}
	printdata(data);
}
main();
