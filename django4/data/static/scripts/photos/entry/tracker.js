//<script id="tracker" type="text/javascript" language="javascript">
 /**  Observing form's state: changed/unchanged
  *   should have an element with an appropriate initial style, e.g.:
  *   <input id="idField" value="" style="background-color: white" /> [or red?]
  *   To be initialized onLoad: tracker = document.getElementById('sys_Id');
  *   String variables (saved/changed) are used for its two alternative styles 
  *   Not hardcoded: form's ID = 'form'
  *               tracker's ID = 'sys_Id' // not needed here: moved to in IniDoc()
  *                  className = 'track'
  *   all variables moved to another SCRIPT
  *   version: 7/8/2005 12:42 PM
  */
  
  
  /** input.onChange="track(changed)"
  *   reset/submit.onClick="track(saved)"  */ 
  function track( state ) {
    if ( (state == saved) || (state == changed) ) {
//tracker = document.getElementById('sys_Id');
tracker.style.backgroundColor= state;
//alert('tracked ' + state);
    }
    else {// never reach
      alert('unexpected error');
      return false;
    }
  }
  
  /** called by NextImage() or other functions */
  function IsSaved() {
     var state = (tracker.style.backgroundColor == saved) ? true : false;
     return state;
  }
  
  /** call retriveOld(this) when needed */
  function retriveOld(object) {
    object.value=object.oldvalue;
    track( changed );
  }
  
  /** input:submit.onClick (can run only before submitting?) */
  function trackValues() {
    //debug = true;
    //alert(debug);
    frm = document.getElementById('form1');
    //if (debug) alert('running trackvalues ' + frm.elements.length + ' !');
       for (i = 0; i < frm.elements.length; i++) {
         if (frm.elements[i].className == classTracker ) {
            frm.elements[i].oldvalue=frm.elements[i].value;
	    //alert(frm.elements[i].name + ' set ' + frm.elements[i].value);
         }
         else {  }
     }
     //alert('tracked values');
   
  }


