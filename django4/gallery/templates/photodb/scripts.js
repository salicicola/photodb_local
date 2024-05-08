
var debug = false;
var start = new Date();
function write_info() {
//			currently = new Date();
//			loaded = currently - start;
//			document.getElementById('feedback_form.at').value = currently.toString();
//			document.getElementById('feedback_form.url').value = escape(location);			
//			document.getElementById('feedback_form.image.url').value = document.images[document.images.length-1].src;
//			document.getElementById('feedback_form.loaded').value = loaded;
}

function feedback() {
  if (document.all) {
		var inner_html = document.getElementById('div.feedback_form').innerHTML;
		w = window.open();
		w.document.write(inner_html);
		w.document.close();
  }
	else {
		document.getElementById('div.feedback_form').style.display = 'block';
  }	
}
		
		
	function changeLocation(o) {
			if (document.getElementById('role').value == 'locality') { 
				//alert(document.getElementById('role').value);
				//document.getElementById('LCID').disabled=0;
				document.getElementById('LCID').value=o.value.split('#')[0];
				document.getElementById('LCID').title=o.value.split('#')[2];
				//document.getElementById('LCID').readonly=1;
				document.getElementById('editcaption').value=o.value.split('#')[1];
				o.style.backgroundColor='red';
				document.getElementById('LCID').style.color='red';
			}
			else {
				alert('to enable feature edit location');
				document.getElementById('LCID').disabled=1;
				o.disabled=1;
				o.parentNode.style.visibility = 'hidden';
			}
	}
		
		var isVerified = "";
//		var herbID = "";
		  function getMissing() {
				missing = location.search;
				missing = missing.split(':')[1];
				missing = missing.split('&')[0];
				missing = missing.split('/')[3];
				document.getElementById('subject').value = 'missing=' + missing;
				s = document.getElementById('hidden_form').innerHTML;
				//alert(s);
				x = window.open();
				x.document.write(s);
				x.document.close();			
			}
		
      function edit_view() {
try {
        document.getElementById('hidden_form').style.display='block';
}
catch (e) {
//alert(e);
}
      }
    
      function normal_view() {
        document.getElementById('hidden_form').style.display='none';
      }
    
      function edit(tag) {
try {
		    if (document.getElementById('hidden_form').style.display=='block') {
		      alert("Submit or Cancel before editing another text block!")
			  }			
			  else {
					var att_number = document.getElementById('att_number').innerHTML;
					var id=tag.id;
					var role=tag.className;
					var content = tag.innerHTML;
					document.getElementById('id').value=id;
					document.getElementById('editcaption').value=content;
					document.getElementById('role').value=role;
					document.getElementById('image_number').value=att_number;
					/// XXX
					//alert(isVerified);
					//alert(document.getElementById('verified').selectedIndex);
					if (isVerified == 'yes') document.getElementById('verified').selectedIndex = 1;
					if (isVerified == 'no') document.getElementById('verified').selectedIndex = 2;
					//alert(document.getElementById('verified').selectedIndex);
//					document.getElementById('herb_id').value=herbID;
					edit_view();
				}
}
catch (e) {
//alert (e);
}
      }
      
      function writeNote() {
        var s = "[<u>Running on localhost: if authorized, click text to edit captions</u>] ";
        document.write(s);
      }
      
      function fillForm() {
        var url=location.href;
        document.getElementById('url').value=url;
      }
      
      function openImage(image) {
        var source = image.src; //, null, "status=yes,toolbar=no,menubar=no,location=no"
        window.open(source);
      }
			
			function reload(mode) {
				 var to = location.href + "&mode=" + mode;
				 window.location.href= to;
			}
			
			function updateURL(thisInput) {
			   var suffix=thisInput.value;
			   var url = document.getElementById('url').value;
//alert(url);
//alert(window.location.href);
//alert(window.location.protocol);
//alert(window.location.hostname);
//alert(window.location.port);
//alert(window.location.pathname);
//path = window.location.pathname
///// assuming that port is not 80
newurl = window.location.protocol + "//" + window.location.hostname + ":" + window.location.port + path.substr(0, 50) + suffix
//alert(newurl)
//var tokens = url.split('/')
//var imid = tokens[8]
//alert(tokens);
//alert(imid);
//         var n = url.indexOf("$canon");
//				 url=url.substr(0, n+9);
//				 url = url + suffix + '.jpg';
				 document.getElementById('url').value = newurl;
}
 
      function stub() {
      
      }
			function duplicate() {
			  if (document.getElementById('append').checked == true) {
				        if (confirm('are you sure to duplicate image? if so be sure to change suffix')) {
			            document.getElementById('mode').value='duplicate';
								}
								else {
								  return false;
								}
				}
				else {
								document.getElementById('mode').value='change';
				}
				/* // no more 'remove' checkbox
				if (document.getElementById('remove').checked == true)	{
				   if (document.getElementById('image_number').value > 0) {
					    alert('to remove image from the site, "image_number" should not be positive');
							return false;
					 }
					 else {
					   if (confirm('are you sure to remove image?')) {
						   document.getElementById('toremove').value = 1;
							 alert('logging yet not implemented');
						 }
						else {
						   return false;
						}
					   }
				   } */
			}
var url_copy_to="/photodb/copyto/?&oldcat={{cat}}&spid={{name.pnid}}&imid={{irec.imid}}&newcat="

