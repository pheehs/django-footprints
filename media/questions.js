"use strict";
/*
questions.js
/*/

var hide_mode = "en";

function createXMLHttpRequest() {
    if (window.XMLHttpRequest) { // other than IE
	return new XMLHttpRequest();
    } else if (window.ActiveXObject) {
	try { //IE6 ~
	    return new ActiveXObject('Msxml2.XMLHTTP');
	} catch (e) {
	    try { //~ IE5
		return new ActiveXObject('Microsoft.XMLHTTP');
	    } catch (e2) {
		return null;
	    }
	}
    } else {
	return null;
    }
}

function onclick_start(action) {
    var form = document.exam;
    
    form.action = action
    form.submit()
}

function link_to_word(qnum) {
    window.location="/ontan/wordquestions/" + (parseInt((qnum-1) / 100) + 1) + "/#question" + qnum;
}

function link_to_fill(qnum) {
    window.location="/ontan/fillquestions/" + (parseInt((qnum-1) / 100) + 1) + "/#question" + qnum;
}

function change_lang(is_exam, session_save){
    var all_tr = document.getElementsByTagName("tr");

    if (is_exam){
	for (var i = 1;i < all_tr.length;i++){
	    show_word(all_tr[i].childNodes[0].innerHTML.slice(0, all_tr[i].childNodes[0].innerHTML.indexOf("<")), true);
	}
    } else {
	for (var i = 0;i < all_tr.length;i++){
	    if (i % 26 != 0){
		show_word(all_tr[i].childNodes[0].innerHTML, true);
	    }
	}
    }
    hide_mode = ["en","ja"][document.getElementById("lang_select").selectedIndex];
    if (is_exam){
	for (var i = 1;i < all_tr.length;i++){
	    hide_word(all_tr[i].childNodes[0].innerHTML.slice(0, all_tr[i].childNodes[0].innerHTML.indexOf("<")));
	}
    } else {
	for (var i = 0;i < all_tr.length;i++){
	    if (i % 26 != 0){
		hide_word(all_tr[i].childNodes[0].innerHTML);
	    }
	}
    }
    if (session_save){
	// send change to server
	// ajax request
	var request = createXMLHttpRequest();
	
	request.onreadystatechange = function () {
	    if (request.readyState == 4 && request.status == 200) {
		//console.log("[*] saved lang in session.");
	    }
	}
	request.open('GET', '/ontan/change_lang?lang=' + hide_mode, true);
	request.send('');
    }
}

function change_mode() {
    var all_tr = document.getElementsByTagName("tr");
    
    switch (document.getElementById("mode_select").selectedIndex) {
    case 0:
	console.log("mouseover_mode")
	for (var i = 1; i < all_tr.length; i++) {
	    all_tr[i].childNodes
	}
	break
    case 1:
        console.log("input_mode")
	break
    }
}

function show_word(qnum, in_change){
    var question_tr = document.getElementById("question"+qnum);
    var childs = question_tr.childNodes;
    if (in_change == true) { var color = "color:#000000;"; }
    else {var color = "color:#FF3300;";}

    switch (hide_mode){
    case "en":
	childs[2].style.cssText = color;
	break;
    case "ja":
	childs[1].style.cssText = color;
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
    
    blank_span.style.cssText = "color:#FF3300;";
}

function hide_fill(blankid){
    var blank_span = document.getElementById("blank"+blankid);
    
    blank_span.style.cssText = "color:#FFFFFF;";
}

function show_all_fill(qnum){
    var all_blank = document.getElementById("question"+qnum).getElementsByTagName("span");
    
    for (var i = 0; i < all_blank.length; i++){
	show_fill(all_blank[i].id.replace("blank", ""));
    }
}

function hide_all_fill(qnum){
    var all_blank = document.getElementById("question"+qnum).getElementsByTagName("span");

    for (var i = 0; i < all_blank.length; i++){
	hide_fill(all_blank[i].id.replace("blank", ""));
    }
}
