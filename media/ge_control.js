"use strict";
/*
ge_control.js
/*/

var Placemarks = {};
var LineStrings = {};
var UHListFlag = {};

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

function addUIHtml(html) {
    document.getElementById('ge_UI').innerHTML += html;
}

var ge;
google.load('earth', '1');

function initCallback(instance) {
    ge = instance;
    ge.getWindow().setVisibility(true);
    //ge.getWindow().setStatusBarVisibility(true);

    // add a navigation control
    ge.getNavigationControl().setVisibility(ge.VISIBILITY_AUTO);

    // add some layers
    ge.getLayerRoot().enableLayerById(ge.LAYER_BORDERS, true);
    ge.getLayerRoot().enableLayerById(ge.LAYER_ROADS, true);
    ge.getLayerRoot().enableLayerById(ge.LAYER_TERRAIN, true);
    ge.getLayerRoot().enableLayerById(ge.LAYER_BUILDINGS, true);
    ge.getLayerRoot().enableLayerById(ge.LAYER_BUILDINGS_LOW_RESOLUTION, true);

    var la = ge.createLookAt('');
    la.setLongitude(139.451572);
    la.setLatitude(35.411797);
    la.setRange(3000000.0);
    ge.getView().setAbstractView(la);

    setInterval(function () {
	var streamingPercent = ge.getStreamingPercent();
	var progressBar = document.getElementById('progress-bar');
	if (streamingPercent == 100) {
	    // streaming complete, hide the progress bar
	    progressBar.style.backgroundColor = '#0f0';
	    progressBar.style.width = '100%';
	} else {
	    // show the progress bar, max width is 250 as per the stylesheet
	    progressBar.style.backgroundColor = '#00f';
	    progressBar.style.width = (100 * streamingPercent / 100) + '%';
	}
    }, 100);
}

function failureCallback(errorCode) {
    alert('GoogleEarthError:' + errorCode);
}

function init() {
    google.earth.createInstance('map3d', initCallback, failureCallback);

    addUIHtml('<div id="progress-wrap">' +
	      '  <div id="progress-explain">' +
	      '    Data Streaming Progress:' +
	      '  </div>' +
	      '  <div id="progress-container">' +
	      '    <div id="progress-bar"></div>' +
	      '  </div>' +
	      '</div><br/>'
	     );
}
google.setOnLoadCallback(init);

function createPlacemark(uh_pk, name, coord, ss_pk) {
    var lplacemark = Placemarks[ss_pk];

    if (lplacemark == undefined) {
	// Create new placemark
	var placemark = ge.createPlacemark('');
	placemark.setName(name);

	// Create style map for placemark
	var icon = ge.createIcon('');
	icon.setHref('http://maps.google.com/mapfiles/kml/paddle/red-circle.png');
	var style = ge.createStyle('');
	style.getIconStyle().setIcon(icon);
	placemark.setStyleSelector(style);

	// Create point
	var point = ge.createPoint('');
	point.setLongitude(coord[0]);
	point.setLatitude(coord[1]);
	placemark.setGeometry(point);
	// database primary key
	placemark.ss_pk = ss_pk
	// Save in Placemarks
	Placemarks[ss_pk] = [placemark, {
	    "uh_pks" : [], 
	    "title_html" : '<span id="balloon_station_name">' + name + '</span><div id="balloon_enter_html">',
	    "enter_html" : [], 
	    "footer_html" : '</div><span id="balloon_correct_link"><a href="#" onclick="correctStation(' + ss_pk + ');">駅座標の訂正</a></span>'
	} ];
	lplacemark = Placemarks[ss_pk];
    }
    if (lplacemark[1]["uh_pks"].length >= 0) {
	Placemarks[ss_pk][1]["uh_pks"].push(uh_pk);
	
	getBalloonData(lplacemark[0].ss_pk);
	
	if (lplacemark[1]["uh_pks"].length == 1) {
	    ge.getFeatures().appendChild(lplacemark[0]);
	    // listen to the click event
	    google.earth.addEventListener(lplacemark[0], 'click', showBalloon);
	    return 1;
	}
    } else {
	alert('Error: placemark(' + ss_pk + ')\'s counter is wrong.');
	return -1;
    }
    return 0;
}

function removePlacemark(uh_pk, ss_pk) {
    var lplacemark = Placemarks[ss_pk];

    if (lplacemark == undefined) {
	alert('Error: placemark(' + ss_pk + ') not defined.');
	return -1;
    } else {
	if (lplacemark[1]["uh_pks"].length > 0) {
	    var index = lplacemark[1]["uh_pks"].indexOf(uh_pk);
	    Placemarks[ss_pk][1]["uh_pks"].splice(index, 1)
	    
	    if (lplacemark[1]["uh_pks"].length == 0) {
		ge.getFeatures().removeChild(lplacemark[0]);

		// remove event listener
		google.earth.removeEventListener(lplacemark[0], 'click', showBalloon);
		return 1;
	    } else {
		getBalloonData(lplacemark[0].ss_pk);
	    }
	}
    }
    return 0;
}

function createLineString(in_coord, out_coord) {
    var linePlacemark = LineStrings['' + in_coord[0] + in_coord[1] + out_coord[0] + out_coord[1]];
    if (linePlacemark == undefined) {
	// Create the placemark
	linePlacemark = ge.createPlacemark('');
	
	// Create the LineString; set it to extend down to the ground
	// and set the altitude mode
	var lineString = ge.createLineString('');
	linePlacemark.setGeometry(lineString);
	lineString.setExtrude(true);
	lineString.setAltitudeMode(ge.ALTITUDE_CLAMP_TO_GROUND);
	
	// Add LineString points
	lineString.getCoordinates().pushLatLngAlt(in_coord[1], in_coord[0], 0);
	lineString.getCoordinates().pushLatLngAlt(out_coord[1], out_coord[0], 0);

	// Create a style and set width and color of line
	linePlacemark.setStyleSelector(ge.createStyle(''));
	var lineStyle = linePlacemark.getStyleSelector().getLineStyle();
	lineStyle.setWidth(5);
	lineStyle.getColor().set('990000FF'); // aabbggrr format
	
	// Save in LineStrings
	LineStrings['' + in_coord[0] + in_coord[1] + out_coord[0] + out_coord[1]] = linePlacemark;
    }
    // Add the feature to Earht
    ge.getFeatures().appendChild(linePlacemark);
}

function removeLineString(in_coord, out_coord) {
    var linePlacemark = LineStrings['' + in_coord[0] + in_coord[1] + out_coord[0] + out_coord[1]];
    if (linePlacemark == undefined) {
	alert('Error: linePlacemark(' + 
	      in_coord[0] + in_coord[1] + out_coord[0] + out_coord[1] + 
	      ') not defined.');
    } else {
	ge.getFeatures().removeChild(linePlacemark);
    }
}

function getUHData(uh_pk, callback) {
    
    // ajax request
    var request = createXMLHttpRequest();
    
    request.onreadystatechange = function () {
	if (request.readyState == 4 && request.status == 200) {
	    var xmlData = request.responseXML;
	    var error = xmlData.getElementsByTagName('Error')[0];
	    
	    if (error.childNodes[0]) {
		alert('DataBaseError:\n' + error.childNodes[0].nodeValue);
	    }else {
		var stations = xmlData.getElementsByTagName('Station');
		
		for (var i = 0; i < stations.length; i++) {
		    switch (stations[i].getAttribute('type')) {
		    case 'in':
			var in_name = stations[i].getElementsByTagName('Name')[0].childNodes[0].nodeValue;
			var in_coord = [parseFloat(stations[i].getElementsByTagName('Lon')[0].childNodes[0].nodeValue), 
					parseFloat(stations[i].getElementsByTagName('Lat')[0].childNodes[0].nodeValue)];
			var in_ss_pk = stations[i].getElementsByTagName('SSPK')[0].childNodes[0].nodeValue;
			break;
		    case 'out':
			var out_name = stations[i].getElementsByTagName('Name')[0].childNodes[0].nodeValue;
			var out_coord = [parseFloat(stations[i].getElementsByTagName('Lon')[0].childNodes[0].nodeValue), 
					 parseFloat(stations[i].getElementsByTagName('Lat')[0].childNodes[0].nodeValue)];
			var out_ss_pk = stations[i].getElementsByTagName('SSPK')[0].childNodes[0].nodeValue;
			break;
		    }
		}
		callback(in_name, in_coord, in_ss_pk, out_name, out_coord, out_ss_pk);
	    }
	}
    }
    request.open('GET', '/footprints/get_lonlat?uh=' + uh_pk, true);
    request.send('');
}

function getBalloonData(ss_pk) {
    // ajax request
    var request = createXMLHttpRequest();
    var lplacemark = Placemarks[ss_pk];
    var URL = '/footprints/get_balloon?station_pk=' + ss_pk + "&uh_pks=" + lplacemark[1]["uh_pks"].join(",");
    
    request.onreadystatechange = function () {
	if (request.readyState == 4 && request.status == 200) {
	    var xmlData = request.responseXML;
	    var error = xmlData.getElementsByTagName('Error')[0];
	    
	    if (error.childNodes[0]) {
		alert('DataBaseError:\n' + error.childNodes[0].nodeValue);
	    }else {
		var balloons = xmlData.getElementsByTagName("Balloon");
		
		Placemarks[ss_pk][1]["enter_html"] = [];
		
		for (var i = 0; i < balloons.length; i++){
		    var date = balloons[i].getElementsByTagName("Date")[0].childNodes[0].nodeValue;
		    var uh_pk = balloons[i].getElementsByTagName("UHPK")[0].childNodes[0].nodeValue;

		    switch (balloons[i].getAttribute('type')) {
		    case "in":
			Placemarks[ss_pk][1]["enter_html"].push('<span bgcolor="#FFFFFF" onmouseover="style.background=\'#00FF00\'" onmouseout="style.background=\'#FFFFFF\'"><b>' + date + '</b>　<span id="balloon_enter_in">入場</span></span><br />');
			break;
		    case "out":
			Placemarks[ss_pk][1]["enter_html"].push('<span bgcolor="#FFFFFF" onmouseover="style.background=\'#00FF00\'" onmouseout="style.background=\'#FFFFFF\'"><b>' + date + '</b>　<span id="balloon_enter_out">出場</span></span><br />');
			break;
		    }
		}
	    }
	}
    }
    request.open('GET', URL, true);
    request.send('');
}

function showBalloon(event) {
    var placemark = event.getCurrentTarget()
    var lplacemark = Placemarks[placemark.ss_pk];
    // Prevent default balloon from popping up for marker placemarks
    event.preventDefault();
    if (lplacemark == undefined) {
	alert("Not found placemark:" + placemark.ss_pk );
    } else {
	
	// wrap alerts in API callbacks and event handlers
	// in a setTimeout to prevent deadlock in some browsers
	setTimeout(function() {
	    var balloon = ge.createHtmlStringBalloon('');
	    balloon.setBackgroundColor("3300FF00");
	    balloon.setFeature(placemark); 
	    //balloon.setMaxWidth(300);
	    balloon.setContentString(lplacemark[1]["title_html"] + lplacemark[1]["enter_html"].join("") + lplacemark[1]["footer_html"]);
	    ge.setBalloon(balloon);

	}, 0);
	
    }
}

function onUHClick(uh_pk) {
    var uh_tr = document.getElementById('UH_' + uh_pk);
    
    // close any balloons
    ge.setBalloon(null);
    
    if (UHListFlag[uh_pk] == false || UHListFlag[uh_pk] == undefined) {
	// show on
	UHListFlag[uh_pk] = true;
	// table tr bgcolor
	uh_tr.setAttribute('bgcolor', '#2B64FF');
	uh_tr.setAttribute('onmouseover', "style.background='#2BCEFF'");
	uh_tr.setAttribute('onmouseout', "style.background='#2B64FF'");
	
	// ajax
	getUHData(uh_pk, function (in_name, in_coord, in_ss_pk, out_name, out_coord, out_ss_pk) {
	    createPlacemark(uh_pk, in_name, in_coord, in_ss_pk);
	    createPlacemark(uh_pk, out_name, out_coord, out_ss_pk);
	    createLineString(in_coord, out_coord);
	});
    } else {
	// show off
	UHListFlag[uh_pk] = false;
	// table tr bgcolor
	uh_tr.setAttribute('bgcolor', '#365178');
	uh_tr.setAttribute('onmouseover', "style.background='#3577E8'");
	uh_tr.setAttribute('onmouseout', "style.background='#365178'");
	
	// ajax
	getUHData(uh_pk, function (in_name, in_coord, in_ss_pk, out_name, out_coord, out_ss_pk) {
	    removePlacemark(uh_pk, in_ss_pk);
	    removePlacemark(uh_pk, out_ss_pk);
	    removeLineString(in_coord, out_coord);
	});
    }
}

var dragInfo = null;
var drag_ss_pk = null;

function correctStation(ss_pk) {
    var lplacemark = Placemarks[ss_pk];
        
    if (lplacemark == undefined) {
	alert("Error! \nplacemark(" + ss_pk + ") not defined.");
    } else {
	drag_ss_pk = ss_pk;
	
	// listen for mousedown on the window (look specifically for point placemarks)
	google.earth.addEventListener(ge.getWindow(), 'mousedown', Drag_mousedown);
	// listen for mousemove on the globe
	google.earth.addEventListener(ge.getGlobe(), 'mousemove', Drag_mousemove);
	// listen for mouseup on the window
	google.earth.addEventListener(ge.getWindow(), 'mouseup', Drag_mouseup);

	var balloon = ge.createHtmlStringBalloon('');
	balloon.setBackgroundColor("3300FF00");
	balloon.setFeature(lplacemark[0]);
	//balloon.setMaxWidth(300);
	balloon.setContentString(lplacemark[1]["title_html"] + lplacemark[1]["enter_html"].join("") + '</div><button type="button" onclick="Drag_end();" >決定</button>');
	ge.setBalloon(balloon);
	console.log("correctStation");
	
	// remove event listener of placemark
	google.earth.removeEventListener(lplacemark[0], 'click', showBalloon);
    }	
}

function Drag_mousedown(event) {
    var placemark = event.getTarget();
    if (placemark.getType() == 'KmlPlacemark' &&
	placemark.getGeometry().getType() == 'KmlPoint') {
	console.log("Drag_mousedown");
	event.preventDefault();
	
	if (dragInfo == null) {
	    if (placemark.ss_pk == drag_ss_pk) {
		placemark.old_coord = [placemark.getGeometry().getLongitude(), placemark.getGeometry().getLatitude()];
		dragInfo = {
		    placemark: event.getTarget(),
		    dragged: false,
		    paused: false
		};
	    }
	} else if (dragInfo.paused == true){
	    dragInfo.paused = false;
	}
    }
}

function Drag_mousemove(event) {
    if (dragInfo) {
	if (dragInfo.paused == false) {
	    console.log("Drag_mousemove");
	    event.preventDefault();
	    
	    var point = dragInfo.placemark.getGeometry();
	    point.setLatitude(event.getLatitude());
	    point.setLongitude(event.getLongitude());
	    dragInfo.dragged = true;
	}
    }
}

function Drag_mouseup(event) {
    if (dragInfo) {
	if (dragInfo.dragged == true && dragInfo.paused == false) {
	    console.log("Drag_mouseup");
	    // if the placemark was dragged, prevent balloons from popping up
	    event.preventDefault();
	    dragInfo.paused = false;
	    dragInfo.paused = true;
	    
	    var balloon = ge.createHtmlStringBalloon('');
	    balloon.setBackgroundColor("3300FF00");
	    balloon.setFeature(lplacemark[0]);
	    //balloon.setMaxWidth(300);
	    balloon.setContentString(lplacemark[1]["title_html"] + lplacemark[1]["enter_html"].join("") + '</div><button type="button" onclick="Drag_end();" >決定</button>');
	    ge.setBalloon(balloon);
	}
    }
}

function Drag_end() {
    if (dragInfo) {
	console.log("Drag_end");
	// remove EventListener
	google.earth.removeEventListener(ge.getWindow(), 'mousedown', Drag_mousedown);
	google.earth.removeEventListener(ge.getGlobe(), 'mousemove', Drag_mousemove);
	google.earth.removeEventListener(ge.getWindow(), 'mouseup', Drag_mouseup);
	
	var placemark = dragInfo.placemark;
	var lplacemark = Placemarks[placemark.ss_pk];
	var lat = placemark.getGeometry().getLatitude()
	var lon = placemark.getGeometry().getLongitude()

	var yesno = confirm(placemark.getName() + "の訂正" + 
			    "変更前(" + placemark.old_coord[0] + placemark.old_coord[1] + ")" + 
			    "変更後(" + lon + lat + ")" + 
			    "を送信しますか？");
	if (yesno = true) {
	    sendCorrection(placemark.ss_pk, lon, lat);
	} else {
	    alert("変更がキャンセルされました。");
	}
	// restore original coord
	placemark.getGeometry().setLongitude(placemark.old_coord[0])
	placemark.getGeometry().setLatitude(placemark.old_coord[1])
	// popup normal balloon
	var balloon = ge.createHtmlStringBalloon('');
	balloon.setBackgroundColor("3300FF00");
	balloon.setFeature(placemark); 
	//balloon.setMaxWidth(300);
	balloon.setContentString(lplacemark[1]["title_html"] + lplacemark[1]["enter_html"].join("") + lplacemark[1]["footer_html"]);
	ge.setBalloon(balloon);
	dragInfo = null;
	// add event listener of placemark
	google.earth.addEventListener(lplacemark[0], 'click', showBalloon);
	
    }
}

function sendCorrection(ss_pk, lon, lat) {
    // ajax request
    var request = createXMLHttpRequest();
    var lplacemark = Placemarks[ss_pk];
    var URL = '/footprints/send_correction?station_pk=' + ss_pk + "&lon=" + lon + "&lat=" + lat;
    
    request.onreadystatechange = function () {
	if (request.readyState == 4 && request.status == 200) {
	    var xmlData = request.responseXML;
	    var error = xmlData.getElementsByTagName('Error')[0];
	    
	    if (error.childNodes[0]) {
		alert('DataBaseError:\n' + error.childNodes[0].nodeValue);
	    }else {
		var balloons = xmlData.getElementsByTagName("Balloon");
		
	    }
	}
    }
    request.open('GET', URL, true);
    request.send("");
}