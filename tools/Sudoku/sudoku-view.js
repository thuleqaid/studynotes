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
function getRelationId(currentid) {
   var thisid=currentid;
   var idlist=new Array(3);
   var i;
   idlist[0]=getGroupId(currentid,1);
   idlist[1]=getGroupId(currentid,2);
   idlist[2]=getGroupId(currentid,3);
   for(i=0;i<idlist[1].length;i++) {
       idx=idlist[0].indexOf(idlist[1][i]);
       if(idx>=0) {
           idlist[0].splice(idx,1);
       }
   }
   for(i=0;i<idlist[2].length;i++) {
       idx=idlist[0].indexOf(idlist[2][i]);
       if(idx>=0) {
           idlist[0].splice(idx,1);
       }
       idx=idlist[1].indexOf(idlist[2][i]);
       if(idx>=0) {
           idlist[1].splice(idx,1);
       }
   }
   idx=idlist[2].indexOf(currentid-0);
   if(idx>=0) {
       idlist[2].splice(idx,1);
   }
   return idlist;
}
