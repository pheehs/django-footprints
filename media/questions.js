"use strict";
/*
questions.js
/*/

var hide_mode = "en";

function change_mode(){
    var all_tr = document.getElementsByTagName("tr");
    
    for (var i = 1;i < all_tr.length;i++){
	show_word(all_tr[i].childNodes[0].innerHTML);
    }
    hide_mode = ["en","ja"][document.getElementById("hide_select").selectedIndex];
    for (var i = 1;i < all_tr.length;i++){
	hide_word(all_tr[i].childNodes[0].innerHTML);
    }

}
function show_word(qnum){
    var question_tr = document.getElementById("question"+qnum);
    var childs = question_tr.childNodes;

    switch (hide_mode){
    case "en":
	childs[2].style.cssText = "color:#000000;";
	break;
    case "ja":
	childs[1].style.cssText = "color:#000000;";
	break;
    }
}

function hide_word(qnum){
    var question_tr = document.getElementById("question"+qnum);
    var childs = question_tr.childNodes;

    switch (hide_mode){
    case "en":
	childs[2].style.cssText = "color:#FFFFFF;";
	break;
    case "ja":
	childs[1].style.cssText = "color:#FFFFFF;";
	break;
    }

}

function show_fill(blankid){
    var blank_span = document.getElementById("blank"+blankid);
    
    blank_span.style.cssText = "color:#000000;";
}

function hide_fill(blankid){
    var blank_span = document.getElementById("blank"+blankid);
    
    blank_span.style.cssText = "color:#FFFFFF;";
}