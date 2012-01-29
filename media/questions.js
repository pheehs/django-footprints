"use strict";
/*
questions.js
/*/

var hide_mode = "en";

$(function(){
    $("form#header-login > input[name='username']").val("ユーザー名").css("color", "#CCC").one("focus", function(){
	$(this).val("").css("color", "#000");
    }).blur(function(){
	if($(this).val() == ""){
	    $(this).val("ユーザー名").css("color", "#CCC").one("focus", function(){
		$(this).val("").css("color", "#000");
	    })
	}
    });
    $("form#header-login > input[name='password']").val("*******").css("color", "#CCC").one("focus", function(){
	$(this).val("").css("color", "#000");
    }).blur(function(){
	if($(this).val() == ""){
	    $(this).val("*******").css("color", "#CCC").one("focus", function(){
		$(this).val("").css("color", "#000");
	    })
	}
    });
    $("form#header-login").submit(function(){
	var username = $("form#header-login > input[name='username']");
	var password = $("form#header-login > input[name='password']");
	if((username.val() == "") || (username.val() == "ユーザー名")){
	    username.css("border", "1px solid blue");
	    $("#top-message").text("ユーザー名を入力してください").fadeIn("slow");
	    return false;
	}else{
	    username.css("border", "");
	}
	if((password.val() == "") || (password.val() == "*******")){
	    password.css("border", "1px solid blue");
	    $("#top-message").text("パスワードを入力してください").fadeIn("slow");
	    return false;
	}else{
	    password.css("border", "");
	}
	$.post("/ontan/accounts/login_ajax/", 
	       {username: username.val(), password: password.val(), csrfmiddlewaretoken: $("#csrfmiddlewaretoken").val()}, 
	       function(data){
		   if (data == "1"){
		       window.location.reload();
		   }else{
		       $("#top-message").text(data).fadeIn("slow");
		   }
	       });
	return false;
    });
    $(".logout").click(function(){
	$.get("/ontan/accounts/logout/", null,
	      function(data){
		  if (data == "1"){
		      window.location.reload();
		  }else{
		      $("#top-message").text(data).fadeIn("slow");
		  }
	      })
    });

    if (window.location.pathname.indexOf("word") != -1){ // on wordquestion
	$(".question").dblclick(function(){
	    $.post("/ontan/add_to_checkedlist", 
		   {qnum: $(this).attr("id").replace("question", ""),
		    csrfmiddlewaretoken: getCookie("csrftoken") },
		   function(data){
		       $("#top-message").text(data).fadeIn("slow");
		   } );
	}).hover(function(){
	    show_word($(this).attr("id").replace("question", ""), false);
	    
	}, function(){
	    hide_word($(this).attr("id").replace("question", ""));
	});

	$(".qnum").click(function(){
	    link_to_fill($(this).parent(".question").attr("id").replace("question", ""));
	});
    }else{ // on fillquestion
	$(".question").dblclick(function(){
	    $.post("/ontan/add_to_checkedlist", 
		   {qnum: $(this).attr("id").replace("question", ""),
		    csrfmiddlewaretoken: getCookie("csrftoken") },
		   function(data){
		       $("#top-message").text(data).fadeIn("slow");
		   } );
	});
	$(".qnum").click(function(){
	    link_to_word($(this).parent(".question").attr("id").replace("question", ""));
	}).hover(function(){
	    show_all_fill($(this).parent(".question").attr("id").replace("question", ""));
	}, function(){
	    hide_all_fill($(this).parent(".question").attr("id").replace("question", ""));
	});
	$(".hid_answer").hover(function(){
	    show_fill($(this).attr("id").replace("blank", ""));
	}, function(){
	    hide_fill($(this).attr("id").replace("blank", ""));
	});
    }

/*    $("#header a").click(function(){
	$("#main-contents").data("href", $(this).attr("href")).hide("fast", function(){
	    $("#main-contents").load(
		$(this).data("href")+ " #main-contents", 
		null, function(){
		    $("#main-contents").show("fast");
		});
	});
	return false;
    });*/

});
/* ref: https://docs.djangoproject.com/en/dev/ref/contrib/csrf/ */
function getCookie(name) { 
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
/* endref */
function onclick_start(action) {
    var form = document.exam;
    
    form.action = action
    form.submit()
}

function link_to_word(qnum) {
    window.location="/ontan/question/wordquestions/" + (parseInt((qnum-1) / 100) + 1) + "/#question" + qnum;
}

function link_to_fill(qnum) {
    window.location="/ontan/question/fillquestions/" + (parseInt((qnum-1) / 100) + 1) + "/#question" + qnum;
}

function toggle_qtype(){
    var replaced = location.href.replace("word", "fill");
    
    if (replaced == location.href){
	location.href = replaced.replace("fill", "word");
    }else {
	location.href = replaced;
    }
}
function change_lang(is_exam, session_save){
    if (is_exam){
	$(".question").each(function(){
	    show_word($("td:eq(0)", this).html().slice(0, $("td:eq(0)", this).html().indexOf("<")), true);
	    // "<" for indexOf() is first character of "<em>(section_number)</em>"
	});
    } else {
	$(".question").each(function(){
	    show_word($("td:eq(0)", this).html(), true);
	});
    }
    hide_mode = ["en","ja"][document.getElementById("lang_select").selectedIndex];
    if (is_exam){
	$(".question").each(function(){
	    hide_word($("td:eq(0)", this).html().slice(0, $("td:eq(0)", this).html().indexOf("<")), true);
	});
    } else {
	$(".question").each(function(){
	    hide_word($("td:eq(0)", this).html(), true);
	});
    }
    if (session_save){
	$.get("/ontan/change_lang", {lang: hide_mode}, null);
    }
}
/*
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
}*/

function show_word(qnum, in_change){
    if (in_change == true) { var color = "#000000"; }
    else {var color = "#FF3300";}

    switch (hide_mode){
    case "en":
	$("#question" + qnum + " > td:eq(2)").css("color", color);
	break;
    case "ja":
	$("#question" + qnum + " > td:eq(1)").css("color", color);
	break
    }
}

function hide_word(qnum){
    switch (hide_mode){
    case "en":
	$("#question" + qnum + " > td:eq(2)").css("color", "#FFFFFF")
	break;
    case "ja":
	$("#question" + qnum + " > td:eq(1)").css("color", "#FFFFFF")
	break;
    }
}

function show_fill(blankid){
    $("#blank"+blankid).css("color", "#FF3300");
}

function hide_fill(blankid){
    $("#blank"+blankid).css("color", "#FFFFFF");
}

function show_all_fill(qnum){
    $("#question"+qnum+" span").each(function(){
	show_fill($(this).attr("id").replace("blank", ""));
    });
}

function hide_all_fill(qnum){
    $("#question"+qnum+" span").each(function(){
	hide_fill($(this).attr("id").replace("blank", ""));
    });
}
