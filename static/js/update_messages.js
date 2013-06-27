 
function removeMessages()
{
    var message_list = document.getElementById("message_list");
    while ( message_list.firstChild ){
		 message_list.removeChild(message_list.firstChild)	    
	    
    }     
} 
function removeNewData(){
    var elem = document.getElementById('new_messages');  
    document.body.removeChild(elem);
    return false;
}
 
function loadMessages() {
	 var graphURL = "http://localhost.net:8000/messages?callback=processResult"
    var script = document.createElement("script");
    script.src = graphURL;
    script.id = "new_messages";
    document.body.appendChild(script);
}
 
function getTimeFromId(id){
	id = id.replace('t','');
	id = id.replace('f','');
	return id
}

function getDateFromUnix(timestamp){
 var date = new Date(timestamp*1000);
 var d = date.getDate();
 var m = date.getMonth() + 1;
 var y = date.getFullYear();
 return '' + y + '-' + (m<=9 ? '0' + m : m) + '-' + (d <= 9 ? '0' + d : d); 
 
 }

function getTimeFromUnix(timestamp){
 var date = new Date(timestamp*1000);
 var h = date.getHours();
 var m = date.getMinutes();
 return '' + (h<=9 ? '0' + h : h) + ':' + (m <= 9 ? '0' + m : m); 
 }


function format_messages(messages){
	var frag = document.createDocumentFragment();   

	if (Object.keys(messages).length == 0) {
		di = document.createElement("div");			
		di.innerHTML = "\t\t\t<div class='alert alert-info'>\n"+
                     "\t\t\t<p>Please login to any account first<br>\n"+                   
                     "\t\t\t<small>To login click checkbox on right</small></p></div>\n";
		frag.appendChild(di);
	
	} else {
		ta = document.createElement("table");
		ta.with = "100%";
		ta.class = "table"
		msgDate0 = getDateFromUnix(new Date().getDate()/1000)
		tt = ""			
 		for (m in messages){
 			 
 			 if (messages[m].account == 'facebook' && ! document.getElementById("fbcb").checked ) continue;
 			 if (messages[m].account == 'twitter' && ! document.getElementById("twcb").checked ) continue;

			 message_image = (messages[m].picture ? "<img   width='128' height='128' src='" + messages[m].picture + "'></img>" :"&nbsp;") 			 
 			
 			 
 			 tt = tt + 
 			 "\t\t\t<tr class='navbar-inner' align='left' valign='top'>\n" +
				"\t\t\t\t<td width='20'><i class='icon-"+messages[m].account+"'></i>" +
				"\t\t\t\t<td width='60'>" + getTimeFromUnix(getTimeFromId((m))) + " : </td>\n" +
      		"\t\t\t\t<td width='128'>"+ message_image+"</td>\n" +
      		"\t\t\t\t<td style='font-size: 120%;'> "+messages[m].text+" </td>\n" + 			 
			 "\t\t\t</tr>\n"; 			 
	   }
		ta.innerHTML = tt
		frag.appendChild(ta);
	}
	return frag 
		
}
 
function processResult(messages) {	
	console.log("->processResult : " + Object.keys(messages).length + " messages");
	var message_list = document.getElementById("message_list");
	
	if ( message_list ){
			
		frag = format_messages(messages);
		removeMessages();
   	message_list.appendChild(frag); 
   	removeNewData();			
			
							
	}
}


//   -->
	
