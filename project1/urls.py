from django.conf.urls import patterns, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',

  
    url(r'^messages$',  'project1.views.reloadmessages',  name='reloadmessages'),       
    url(r'^twitter_login_success/$',  'project1.views.twitter_login_success',  name='twitter_login_success'),       
    url(r'^facebook_login_success/$', 'project1.views.facebook_login_success', name='login_success'),       
    url(r'^facebook_login/$', 'project1.views.facebook_login', name='facebook_login'),       
    url(r'^twitter_login/$', 'project1.views.twitter_login', name='twitter_login'),       
    url(r'^$', 'project1.views.index', name='index'),       




)
