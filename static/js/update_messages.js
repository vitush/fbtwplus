 
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
	 console.log("->loadMessages");
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

function processResult(messages) {	
	console.log("->processResult");
	var message_list = document.getElementById("message_list");
	msgDate0 = getDateFromUnix(new Date().getDate()/1000)
	if ( message_list ){
			var frag = document.createDocumentFragment();
			var li;
			if (messages){
 			for (m in messages){
				li = document.createElement("dl");
				li.id = m;
				li.innerHTML = ""
				
				msgDate = getDateFromUnix(getTimeFromId((m)));
				if (msgDate0 != msgDate){
				li.innerHTML = "<dt> &nbsp; </dt><dd><br><center><b>"+msgDate+"</b></center></dd>";
              					 msgDate0 = msgDate;
	
				}				
																	
				if (messages[m].account == 'facebook' && document.getElementById("fbcb").checked ) {
				li.innerHTML = li.innerHTML + "<dt><i class='icon-facebook'></i></dt>" +
              "<dd>[ " + getTimeFromUnix(getTimeFromId((m))) + " ] : <font color='#008000'>"+messages[m].text+"</font> </dd>";				
				}else if (messages[m].account == 'twitter' && document.getElementById("twcb").checked) {
				li.innerHTML = li.innerHTML + "<dt><i class='icon-twitter'></i></dt>" +
              "<dd>[ " + getTimeFromUnix(getTimeFromId((m))) + " ] : <font color='#0000FF'>"+messages[m].text+"</font> </dd>";				
				}	  					
			}
			} else {
				li.innerHTML = "<dd><div class='alert alert-info'>"+
                     "<p>Please login to any account first<br>"+                   
                     "<small>To login click checkbox on right</small></p></div></dd>";
                     
			}
			frag.appendChild(li);     	     	
		   removeMessages();
   		message_list.appendChild(frag); 
   		removeNewData();
	}
}

//   -->
	
