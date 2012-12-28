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

var id_t="",id="";
function toggleGroupClass(currentid,funcname,class0,class1,class2,class3) {
    var idlist=getRelationId(currentid);
    for(var i=0;i<idlist[0].length;i++) {
        $("#"+idlist[0][i])[funcname](class1);
    }
    for(i=0;i<idlist[1].length;i++) {
        $("#"+idlist[1][i])[funcname](class2);
    }
    for(i=0;i<idlist[2].length;i++) {
        $("#"+idlist[2][i])[funcname](class3);
    }
    $("#"+currentid)[funcname](class0);
}
function click_sudoku(clickid) {
    if (id!=="") {
        toggleGroupClass(id,"removeClass","hltd0","hltd1","hltd2","hltd3");
    }
    id=clickid;
    if (id!=="") {
        toggleGroupClass(id,"addClass","hltd0","hltd1","hltd2","hltd3");
    }
}
function clear_sudoku() {
    var sudokutd=$("#sudoku td");
    sudokutd.each(function(idx) {
        $(this).text("");
    });
}
function get_sudoku() {
    var sudokutd=$("#sudoku td");
    var currentdata=new Array();
    var temp;
    sudokutd.each(function(idx) {
        temp=$(this).text();
        if (temp==="") {
            currentdata.push(0);
        } else {
            currentdata.push(0+temp);
        }
    });
    return currentdata;
}
function set_sudoku(indata) {
    var sudokutd=$("#sudoku td");
    var currentdata=new Array();
    var temp;
    sudokutd.each(function(idx) {
        temp=indata[idx];
        if (temp===0) {
            $(this).text("");
        } else {
            $(this).text(temp);
        }
    });
}
function click_sudoku_tool(clickid) {
    if (id_t!=="") {
        $("#"+id_t).removeClass("hltd0");
    }
    if (clickid==="t4") {
        id_t="";
        clear_sudoku();
    } else if(clickid==="t6") {
        id_t="";
    var workarea=new Array(81);
    var counter,data;
    data=get_sudoku();
    makeworkarea(data,workarea);
    counter=solveonce(workarea);
    if(counter>0) {
    	updatebase(workarea,data);
            set_sudoku(data);
            if(countunfinish(data)===0) {
                alert("Finish!");
            }
    } else {
            alert("I cannot solve it any more!");
        }
    } else {
        id_t=clickid;
        if (id_t!=="") {
            $("#"+id_t).addClass("hltd0");
        }
    }
}
function init_sudoku() {
    $("#sudoku").append("<table> \
                             <tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr> \
                             <tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr> \
                             <tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr> \
                             <tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr> \
                             <tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr> \
                             <tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr> \
                             <tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr> \
                             <tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr> \
                             <tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr> \
                         </table>");
    var sudokutd=$("#sudoku td");
    sudokutd.each(function(idx) {
        $(this).attr("id",idx);
        var block=Math.floor(idx/27)*3+Math.floor((idx%9)/3);
        $(this).addClass("block"+block);
    });
    sudokutd.click(function() {
        var currentid=$(this).attr("id");
        click_sudoku(currentid);
    });
}
function init_sudoku_number() {
    $("#sudoku-number").append("<table> \
                             <tr><td>1</td></tr> \
                             <tr><td>2</td></tr> \
                             <tr><td>3</td></tr> \
                             <tr><td>4</td></tr> \
                             <tr><td>5</td></tr> \
                             <tr><td>6</td></tr> \
                             <tr><td>7</td></tr> \
                             <tr><td>8</td></tr> \
                             <tr><td>9</td></tr> \
                             <tr><td></td></tr> \
                         </table>");
    var sudokuntd=$("#sudoku-number td");
    sudokuntd.each(function(idx) {
        $(this).attr("id","n"+idx);
    });
    sudokuntd.click(function() {
        if (id!=="") {
            $("#"+id).text($(this).text());
            click_sudoku_tool("");
            click_sudoku("");
        }
    });
}
function init_sudoku_tool() {
    $("#sudoku-tool").append("<table> \
                             <tr><td>a</td></tr> \
                             <tr><td>b</td></tr> \
                             <tr><td>c</td></tr> \
                             <tr><td>d</td></tr> \
                             <tr><td>Clear</td></tr> \
                             <tr><td>Generate</td></tr> \
                             <tr><td>Solve</td></tr> \
                         </table>");
    var sudokuttd=$("#sudoku-tool td");
    sudokuttd.each(function(idx) {
        $(this).attr("id","t"+idx);
    });
    sudokuttd.click(function() {
        click_sudoku_tool($(this).attr("id"));
    });
}
