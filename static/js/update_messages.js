 
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

function format_date_line(date){
s = "\t\t\t";
line = s+ "<tr  align='center' class='navbar-inner '><td>\n" +
		s+ "\t<div class='row-fluid'>\n" +
		s+ "\t\t<div class='span12'>\n" +
		s+ "\t\t<div class='alert alert-info'><b>"+date + "</b></div> \n" + 
		s+ "\t\t</div>\n" +
		s+ "\t</div>\n" +
		s+ "</td></tr>\n\n"  ;

   return line;
}

 
 
	
function format_msg_line(message,id){

message_account = message.account ;	 
message_text = message.text ;
message_time = getTimeFromUnix(getTimeFromId((m)));
message_description  = (message.description ? message.description :"")
message_name  = (message.name  ? message.name :"")
 
	 
s = "\t\t\t";
line = s+ "<tr align='left' valign='top ' class='navbar-inner'><td>\n" +
		s+ "\t<div class='row-fluid'>\n" +
		s+ "\t\t<div class='span12'>\n" +
		s+ "\t\t<span class='label label-info'><i class='icon-"+message_account+"'></i>&nbsp;&nbsp;&nbsp; "+message_time+
		" : </span>&nbsp;&nbsp;" +   message_text + " \n";
		if (message.link) {
			s2 = "\t\t\t\t\t\t";

			sub_msg = "<table  align='left'><tr align='left'> \n"; 
	      sub_msg = sub_msg +"          <td width='130' >"  + "<a  id='img_"+id+"' href='" + message.link + "'></a></td>\n";
			
			if (message_name != "" || message_description != "" ){
	         sub_msg = sub_msg +"          <td>"
	         if (message_name != "") sub_msg = sub_msg + "<b>" + "<a href='" + message.link + "'>" + message_name + "</a></b><br>\n"; 
	         if (message_description != "") sub_msg = sub_msg  + "<a href='" + message.link + "'>" + message_description + "</a>\n"; 
	         
	         sub_msg = sub_msg +"</td>\n";
			
			}
         sub_msg = sub_msg +" </tr></table>\n";
            
 
   
         if ( message.picture || message_name != "" || message_description != ""  ){
				line = line +
				s2+"<div class='row-fluid'>\n" +
				s2+ "\t<div class='span11 offset1'>\n" +
				s2+ "\t<div class='navbar-inner'>\n" +	
				s2+ s+ sub_msg  + "\n" +
				s2+"\t</div>\n" +
				s2+"\t</div>\n" +
				s2+"</div>\n";
         }   
	
		}

line = line +
		s+ "\t\t</div>\n" +
		s+ "\t</div>\n" +
		s+ "</td></tr>\n\n"  ;

 
   return line;
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
		ta.class = "table";
		msgDate0 = getDateFromUnix(new Date().getDate()/1000)
		tt = ""			
 		for (m in messages){

 
	
			 message_account = messages[m].account ;	 
 			 if (message_account == 'facebook' && ! document.getElementById("fbcb").checked ) continue;
 			 if (message_account == 'twitter' && ! document.getElementById("twcb").checked ) continue;
	
			 message_date = getDateFromUnix(getTimeFromId((m)));
			 if (message_date != msgDate0){
				 tt = tt + format_date_line(message_date);
				 msgDate0 = message_date;			 
			 }			 
			 
			 tt = tt + format_msg_line(messages[m],m);
			 
	   }
		ta.innerHTML = tt
		frag.appendChild(ta);
	}
	return frag 
		
}

function  loadImageCallback(image,parent_id) {
	a = document.getElementById(parent_id);
 		 
 	if (a) a.appendChild(image);
}


function  loadImage(url,parent_id,callback) {
		 	var image = new Image();
 			image.onerror = function () {
 		 		console.log('error loading ' + this.src);
 			};
 			
 			image.onload = function () {
				callback(this,parent_id)
 			};
 			image.src = url;
		
}


function  loadImages(messages) {
 
	for (m in messages){
		if (messages[m].picture){
 	 
 			parent_id = "img_" + m;
			loadImage(messages[m].picture,parent_id,loadImageCallback);
			
		}
	}	
}
 
function processResult(messages) {	
 
	var message_list = document.getElementById("message_list");
	

	if ( message_list ){
			
		frag = format_messages(messages);
		removeMessages();
   	message_list.appendChild(frag);
   	loadImages(messages); 
   	removeNewData();			
			
							
	}
}


//   -->
	
