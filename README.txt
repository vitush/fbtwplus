fbtwplus -  Demo of authorization via Facebook and Twitter and reading of posts.  
            python and django is used.

========

Python 2.7 requered! 

Install requirements:

 1. cd fbtwplus/
 2. pip install -r requirements.txt

Configure:
 1. Add /change hosts file to add DNS name localhost.net pointed to 127.0.0.1. in /etc/hosts 
    ex:	
	"127.0.0.1       localhost.localdomain   localhost  localhost.net" 

Run app:
 1. cd   fbtwplus/
 2. python manage.py runserver

Use app:
  http://localhost.net:8000

App will use current active FB and Twitter accounts or  ask for login if needed.

