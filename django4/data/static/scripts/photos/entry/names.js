// Not for Internet Explorer
// 2011-08-15 18:17:39 
// perhaps global OK
var xData = null;
var xProcessor = null;
//alert('start loading');

function getXHR() {
	try {return new XMLHttpRequest()} catch (e) {};
	return null;
}

var xhr = getXHR();
if (xhr) {
	xhr.open("GET", "/static/scripts/photos/entry/species.xml"); // django urls.py problems with /data/species // XXX for now juist copied it here
	xhr.overrideMimeType("text/xml");
	xhr.onreadystatechange = function () { handleXML(xhr) };
	xhr.send(null);
	var xhr2 = getXHR();
	xhr2.open("GET", "/static/scripts/photos/entry/TDM_names.xsl", "true");
	xhr2.overrideMimeType("text/xml");
	xhr2.onreadystatechange = function () { handleXSLT(xhr2) };
	xhr2.send(null);
}	

//alert('now xhr=' + xhr);
		
function handleXML(xhr) {			
	if (xhr.readyState == 4) {
		if (xhr.status == 200) {
//alert('response' + xhr.responseXML);
			xData = xhr.responseXML;
//alert(xData);
		}
		else {
		}
	}
	else {
	}
}
function handleXSLT(x) {			
	if (x.readyState == 4 && x.status == 200) {
		try {
//alert("XHR2 XSL " + x);
			xProcessor = new XSLTProcessor();
			var xslData = x.responseXML;
//alert(xslData);					
			xProcessor.importStylesheet(xslData);
		}
		catch (e) {
			alert(e);
		}
	}
}

//alert('there')
//alert(xData);
//alert('there 2')
function updateSelect(o) {
//alert('running updateSelect');
	txt = o.value;
	if (txt.length == 1) {
			o.oldvalue=""; // FIXING BUG 
	}
	if (xData && xProcessor && txt.length > 3) {
		var tSelect = null;
		tObject = document.getElementById('x');
		try {
			tSelect = document.getElementById('pnids');
			var left = tSelect.options.length;
			if (left == 2) {
				//alert(left);
				updateName(tSelect);
				//alert('done');
				tObject.innerHTML = "";
				o.blur();	// FIXING bug:: //document.getElementById('caption').focus();
				return;
			}
		}
		catch (e) {}
//		alert('here');
		// FIXME: to check if valid XML (XSL not needed, if xProcessor != null) ?
		try {
			xProcessor.clearParameters();
			xProcessor.setParameter(null, "text", txt);
						// FIXME
			tObject.style.display="";
			var result = xProcessor.transformToFragment(xData, document);
//alert(result.innerHTML);
			tObject.innerHTML = "";
			tObject.appendChild(result);
		}
		catch (e) {
			alert(e);
		}
	}    
	else {
		//
	}
}
function updateName(selectO) {
	document.getElementById('latname').value = selectO.options[selectO.selectedIndex].innerHTML;
	v = selectO.value;
	values = v.split('/');
	document.getElementById('FID').value = values[0];
	document.getElementById('PNID').value = values[1];
	selectO.style.display='none';
	setIndID();
}
//alert('loaded');
						

