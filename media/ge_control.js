"use strict";
/*
ge_control.js
/*/

var Placemarks = {};
var LineStrings = {};

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

    addUIHtml('<style type="text/css">' +
	      '  #progress-wrap { padding-top: 3%; height: 30%; }' +
	      '  #progress-explain { height: 60%; text-align: center;}' +
	      '  #progress-container { width: 50%; height: 40%; border: 1px solid #ccc; margin: 0 auto;}' +
	      '  #progress-bar { width: 0; height: 100%; }' +
	      '</style>' +
	      '<div id="progress-wrap">' +
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

function createPlacemark(pk, name, coord) {
    var lplacemark = Placemarks[name + coord[0] + coord[1]];

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
	// Save in Placemarks
	Placemarks[name + coord[0] + coord[1]] = [placemark, []];
	lplacemark = Placemarks[name + coord[0] + coord[1]];
	// Sort UH_pk list
	//Placemarks[name + coord[0] + coord[1]][1].sort(getUHData_sort)
    }
    if (lplacemark[1].length >= 0) {
	Placemarks[name + coord[0] + coord[1]][1].push(pk);
	if (lplacemark[1].length == 1) {
	    ge.getFeatures().appendChild(lplacemark[0]);

	    // listen to the click event
	    google.earth.addEventListener(lplacemark[0], 'click', showBalloon);
	    return 1;
	}
    } else {
	alert('Error: placemark(' + name + ":" + coord[0] + ", " + coord[1] + ')\'s counter is wrong.');
	return -1;
    }
    return 0;
}

function removePlacemark(pk, name, coord) {
    var lplacemark = Placemarks[name + coord[0] + coord[1]];

    if (lplacemark == undefined) {
	alert('Error: placemark(' + name + ":" + coord[0] + ", " + coord[1] + ') not defined.');
	return -1;
    } else {
	if (lplacemark[1].length > 0) {
	    var index = lplacemark[1].indexOf(pk);
	    Placemarks[name + coord[0] + coord[1]][1].splice(index, 1)

	    if (lplacemark[1].length == 0) {
		ge.getFeatures().removeChild(lplacemark[0]);

		// remove event listener
		google.earth.removeEventListener(lplacemark[0], 'click', showBalloon);
		return 1;
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

function getUHData(pk, need_date, callback) {
    /*
      need_date(boolean) : if true, add date parameter to callback arguments.
     */
    
    // ajax request
    var request = createXMLHttpRequest();
    
    request.onreadystatechange = function () {
	if (request.readyState == 4 && request.status == 200) {
	    var xmlData = request.responseXML;
	    var error = xmlData.getElementsByTagName('Error')[0];
	    
	    if (error.childNodes[0]) {
		alert('DataBaseError:\n' + error.childNodes[0].nodeValue);
	    }else {
		var date = xmlData.getElementsByTagName("Date")[0].childNodes[0].nodeValue;
		var stations = xmlData.getElementsByTagName('Station');
		
		for (var i = 0; i < stations.length; i++) {
		    switch (stations[i].getAttribute('type')) {
		    case 'in':
			var in_name = stations[i].getElementsByTagName('Name')[0].childNodes[0].nodeValue;
			var in_coord = [parseFloat(stations[i].getElementsByTagName('Lon')[0].childNodes[0].nodeValue), 
					parseFloat(stations[i].getElementsByTagName('Lat')[0].childNodes[0].nodeValue)];
			break;
		    case 'out':
			var out_name = stations[i].getElementsByTagName('Name')[0].childNodes[0].nodeValue;
			var out_coord = [parseFloat(stations[i].getElementsByTagName('Lon')[0].childNodes[0].nodeValue), 
					 parseFloat(stations[i].getElementsByTagName('Lat')[0].childNodes[0].nodeValue)];
			break;
		    }
		}
		if (need_date == true) {
		    callback(in_name, in_coord, out_name, out_coord, date);
		}else {
		    callback(in_name, in_coord, out_name, out_coord);
		}
	    }
	}
    }
    request.open('GET', '/footprints/get_lonlat?uh=' + pk, true);
    request.send('');
}

function showBalloon(event) {
    var placemark = event.getCurrentTarget()
    var lplacemark = Placemarks[placemark.getName() + placemark.getGeometry().getLongitude() + placemark.getGeometry().getLatitude()];
    // Prevent default balloon from popping up for marker placemarks
    event.preventDefault();
    if (lplacemark == undefined) {
	alert("Not found placemark:" + placemark.getName() + placemark.getGeometry().getLongitude() + placemark.getGeometry().getLatitude());
    } else {
	
	// wrap alerts in API callbacks and event handlers
	// in a setTimeout to prevent deadlock in some browsers
	setTimeout(function() {
	    var balloon = ge.createHtmlStringBalloon('');
	    var title_html = "<h3>" + placemark.getName() + "</h3><p>";
	    var body_html = "";
	    var footer_html = "</p>";
	    
	    balloon.setFeature(placemark); 
	    //balloon.setMaxWidth(300);
	    for (var i = 0; i < lplacemark[1].length; i++) {
		getUHData(lplacemark[1][i], true, function (in_name, in_coord, out_name, out_coord, date) {
		    if (placemark.getName() == in_name) {
			body_html += "<b>" + date + "</b>　入場<br />";
		    } else if (placemark.getName() == out_name) {
			body_html += "<b>" + date + "</b>　出場<br />";
		    }
		    balloon.setContentString(title_html + body_html + footer_html);
		    ge.setBalloon(balloon);
		});
	    }
	    
	}, 0);
	
    }
}

function onUHClick(pk) {
    var uh_tr = document.getElementById('UH_' + pk);
    
    // close any balloons
    ge.setBalloon(null);
    
    if (uh_tr.getAttribute('bgcolor') == '#365178') {
	// show on
	// table tr bgcolor
	uh_tr.setAttribute('bgcolor', '#2B64FF');
	uh_tr.setAttribute('onmouseover', "style.background='#2BCEFF'");
	uh_tr.setAttribute('onmouseout', "style.background='#2B64FF'");
	
	// ajax
	getUHData(pk, false, function (in_name, in_coord, out_name, out_coord) {
	    createPlacemark(pk, in_name, in_coord);
	    createPlacemark(pk, out_name, out_coord);
	    createLineString(in_coord, out_coord);
	});
    } else if (uh_tr.getAttribute('bgcolor') == '#2B64FF') {
	// show off
	// table tr bgcolor
	uh_tr.setAttribute('bgcolor', '#365178');
	uh_tr.setAttribute('onmouseover', "style.background='#3577E8'");
	uh_tr.setAttribute('onmouseout', "style.background='#365178'");
	
	// ajax
	getUHData(pk, false, function (in_name, in_coord, out_name, out_coord) {
	    removePlacemark(pk, in_name, in_coord);
	    removePlacemark(pk, out_name, out_coord);
	    removeLineString(in_coord, out_coord);
	});
    }
}
