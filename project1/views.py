import json
import urllib2
from django.shortcuts import render 
from urlparse import parse_qsl

from pyfb import Pyfb
from django.http import  HttpResponseRedirect,HttpResponse,HttpResponseForbidden,HttpResponseBadRequest,HttpResponseServerError
from settings import FACEBOOK_APP_ID, FACEBOOK_APP_SECRET, FACEBOOK_REDIRECT_URL
from settings import TWITTER_CUSTOMER_KEY, TWITTER_CUSTOMER_SECRET, TWITTER_AUTHORIZATION_URL,TWITTER_REQUEST_TOKEN_URL,TWITTER_ACCESS_TOKEN_URL

import oauth2 as oauth

from collections import OrderedDict

 

messages = {}
 
facebook = None
facebook_access_token = None

import twitter
twitter_api = None
twitter_oauth_token = None
twitter_oauth_verifier = None
twitter_oauth_consumer  = oauth.Consumer(key=TWITTER_CUSTOMER_KEY, secret=TWITTER_CUSTOMER_SECRET)

twitter_access_token = None

facebook_enabled = False 
twitter_enabled = False
facebook_loaded = False 
twitter_loaded = False

facebook_user = ""
facebook_user_id = None

twitter_user  = ""


import datetime, calendar
date_format_fb = '%Y-%m-%dT%H:%M:%S+0000'

def to_timestamp(fb_date):
    date = datetime.datetime.strptime(fb_date,date_format_fb)
    date_utc = date.utctimetuple() 
    return calendar.timegm(date_utc) # to unix time

def to_ctime(fb_date):
    date = datetime.datetime.strptime(fb_date,date_format_fb)
    return date.ctime()
 
def get_extended_at(short_lived_access_token):
    from facepy.utils import get_extended_access_token
    long_lived_access_token, expires_at = get_extended_access_token(
                                            short_lived_access_token,
                                            FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)        
    return long_lived_access_token
        

        
def twitterLoadMessages(user):
    global twitter_loaded

    if twitter_api == None:
        return False
        
    if twitter_user == None:
        return False
    
    msg_count =0
    try :                
        statuses =  twitter_api.GetUserTimeline(user)
        for s in statuses:
            created = datetime.datetime.fromtimestamp(s.GetCreatedAtInSeconds())
            
            record_key = str(s.GetCreatedAtInSeconds()) + "t"
            record = {'account': "twitter", 
                      'created': created.ctime(), 
                      'text':s.text  }
                    
            messages[ record_key ] = record        
            msg_count = msg_count +1
                
        twitter_loaded = True
        print "Twitter %i messages loaded." %msg_count
    except ValueError:
        print "Twitter - Rate limit exceeded. Ingnoring "                
          
def facebookLoadMessages(user_id):
    global messages_list
    global facebook_loaded

        
    url = 'https://graph.facebook.com/%s/posts?access_token=%s' % (user_id,facebook_access_token)
    req = urllib2.Request(url)
    
    response = urllib2.urlopen(req)
     
    page = response.read() 
    fb_data =  json.loads(page)
    response.close()
    
    msg_count = 0
    for msg in fb_data['data']:
        text = ''
        if msg.has_key('story') :
            text = msg['story']
            
        if msg.has_key('message') :
            text = msg['message']
        
        record_key = str(to_timestamp(msg['created_time']))+"f"
        record = {'account': "facebook", 
                  'created': to_ctime(msg['created_time']), 
                  'text':text  }                
        messages[ record_key ] = record        
        msg_count = msg_count +1
    print "Facebook : %i messages loaded." %msg_count
    
        
    facebook_loaded = True
    
    

def reloadmessages(request): 

    facebookLoadMessages(facebook_user_id)
    twitterLoadMessages(twitter_user)
    
    callback = request.GET.get('callback')
    msgs = json.dumps(sortedMessages(messages))
    
    if callback:
        data = '%s(%s)' % (callback, msgs)
    
    return HttpResponse(data,mimetype="application/x-javascript")

def sortedMessages(messages):
    if  (messages != None):
         return OrderedDict(sorted(messages.items(), key=lambda t: t[0],reverse=True))   
        

def index(request):       
    global facebook_user
    global twitter_user
    global facebook_loaded
    global twitter_loaded 
    global facebook_user_id
    
    if facebook_enabled:    
        if facebook != None:
            if not facebook_loaded:
                me = facebook.get_myself()
                facebook_user = me.name
                facebook_user_id = str(me.id)
                print "facebook_user_id = %s" % facebook_user_id
                facebookLoadMessages(facebook_user_id)
        
    if twitter_enabled:
        if twitter_api != None:
            try :                
                tw_user = twitter_api.VerifyCredentials()
                if tw_user != None:
                    twitter_user = tw_user.screen_name
                    if not twitter_loaded:
                        twitterLoadMessages(twitter_user)

            except ValueError:
                print "Twitter - Rate limit exceeded. Ingnoring "                
 
      
    context = {'messages':   sortedMessages(messages),
               'facebook_enabled': facebook_enabled, 
               'twitter_enabled': twitter_enabled, 
               'facebook_user': facebook_user,
               'twitter_user': twitter_user,
               'facebook_user_id': facebook_user_id,
               'facebook_access_token': facebook_access_token }
                
    return render(request, 'project1/main.html', context) 
                 
                
def facebook_login(request):
    global facebook_enabled    
    global facebook

    fb_check = request.GET.get('facebook_checkbox')  
    if fb_check == None :
        facebook_enabled = False;
        return HttpResponseRedirect("/")
    
    facebook_enabled = True

    if facebook_access_token != None:        
        return HttpResponseRedirect("/")
    
    facebook = Pyfb(FACEBOOK_APP_ID)
    return HttpResponseRedirect(facebook.get_auth_code_url(redirect_uri=FACEBOOK_REDIRECT_URL))
    

def facebook_login_success(request):
    global facebook_access_token
    global facebook_enabled
    code = request.GET.get('code')  
    if code == None:
        return HttpResponseForbidden("Facebook login failed, Return cone = None ")
        
    facebook_access_token = facebook.get_access_token(FACEBOOK_APP_SECRET, code, redirect_uri=FACEBOOK_REDIRECT_URL)
    facebook_enabled = True    
    return HttpResponseRedirect("/")
   
   
def twitter_login(request):
    global twitter_access_token
    global twitter_oauth_token
    global twitter_api
    global twitter_enabled
    
    tw_check = request.GET.get('twitter_checkbox')  
    if tw_check == None :
        twitter_enabled = False
        return HttpResponseRedirect("/")

    twitter_enabled = True
    
    if twitter_access_token != None:
        return HttpResponseRedirect("/")


    oauth_client  = oauth.Client(twitter_oauth_consumer)        
    resp, content = oauth_client.request(TWITTER_REQUEST_TOKEN_URL, 'GET')
    
    if resp['status'] != '200':
        return HttpResponseBadRequest('Invalid respond from Twitter requesting temp token: %s' % resp['status'])

    request_token = dict(parse_qsl(content))  
    twitter_oauth_token =  oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])             
    twitter_auth_url = "%s?oauth_token=%s" %(TWITTER_AUTHORIZATION_URL,request_token['oauth_token'])
    
    return HttpResponseRedirect(twitter_auth_url)
    
   
def twitter_login_success(request):
    global twitter_oauth_token
    global twitter_oauth_verifier
    global twitter_api
    global twitter_access_token
    global twitter_enabled

    twitter_oauth_verifier = request.GET.get('oauth_verifier')  
    if twitter_oauth_verifier  == None:
        return HttpResponseForbidden("Twitter oauth verification code request failed")

    if twitter_oauth_token == None: 
        return HttpResponseServerError("Twitter oauth token failed")

    twitter_oauth_token.set_verifier(twitter_oauth_verifier)  
    
    oauth_client  = oauth.Client(twitter_oauth_consumer, twitter_oauth_token)
    resp, content = oauth_client.request(TWITTER_ACCESS_TOKEN_URL, method='POST', body='oauth_callback=oob&oauth_verifier=%s' % twitter_oauth_verifier)
    twitter_access_token  = dict(parse_qsl(content))

    if resp['status'] != '200':
        return HttpResponseServerError('The request for a Token did not succeed: %s' % resp['status'])
    #else:
    #    return HttpResponse('Your Twitter Access Token key: %s\nAccess Token secret: %s' % (twitter_access_token['oauth_token'],twitter_access_token['oauth_token_secret']))
    print ('Your Twitter Access Token key: %s\r\n Access Token secret: %s' % (twitter_access_token['oauth_token'],twitter_access_token['oauth_token_secret']))

    twitter_api = twitter.Api(consumer_key=TWITTER_CUSTOMER_KEY,
                      consumer_secret=TWITTER_CUSTOMER_SECRET, 
                      access_token_key=twitter_access_token['oauth_token'],
                      access_token_secret=twitter_access_token['oauth_token_secret'])    
    twitter_enabled = True
    return HttpResponseRedirect("/")
   
      
   
   