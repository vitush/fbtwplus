fbtwplus
========

Configure:

	Add /change hosts file to add DNS name localhost.net pointed to 127.0.0.1. in /etc/hosts 
 	ex:	
		"127.0.0.1       localhost.localdomain   localhost  localhost.net" 

To Run app 
 1. cd   fbtwplus/
 2. python manage.py runserver

Access App on 
  http://localhost.net:8000

App will use current active FB and Twitter accounts or  ask for login if needed.

