""" view.py
"""
import json
from collections import OrderedDict
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.http import HttpResponseServerError

from project1.twitteraccount import TwitterAccount
from project1.facebookaccount import FacebookAccount

twitter_account = TwitterAccount()
facebook_account = FacebookAccount()

facebook_enabled = False
twitter_enabled = False

messages = {} # Global message store


def reloadmessages(request):
    """ Return messages in json""" 
    if facebook_account.is_authorized():
        facebook_account.load_messages(messages)
    if twitter_account.is_authorized():
        twitter_account.load_messages(messages)
    callback = request.GET.get('callback')
    msgs = json.dumps(sorted_messages(messages))
    #debug_msgs = json.dumps(sortedMessages(messages),indent=2)
    #print debug_msgs
    if callback:
        data = '%s(%s)' % (callback, msgs)

    return HttpResponse(data, mimetype="application/x-javascript")


def sorted_messages(mess):
    """ Sort messages. 
        Messages of not active accounts will skipped.
    """
    if (mess is not None):
        messages1 = {}
        for key, val in messages.items():
            if key.endswith('f') and facebook_enabled:
                messages1[key] = val
            if key.endswith('t') and twitter_enabled:
                messages1[key] = val

        return OrderedDict(sorted(messages1.items(), 
                                  key=lambda t: t[0], 
                                  reverse=True))


def index(request):
    """ Default request handler"""
    if facebook_enabled:
        if facebook_account.is_authorized():
            facebook_account.load_messages(messages)

    if twitter_enabled:
        if twitter_account.is_authorized():
            twitter_account.load_messages(messages)
    
    context = {'messages': sorted_messages(messages),
               'facebook_enabled': facebook_enabled,
               'twitter_enabled': twitter_enabled,
               'facebook_user': facebook_account.user,
               'twitter_user': twitter_account.user
               }

    return render(request, 'project1/main.html', context)


def facebook_login(request):
    """Handle FB login status (On/Off checkbox)
       Authorize via FB if first request.             
    """
    global facebook_enabled

    fb_check = request.GET.get('facebook_checkbox')
    if fb_check is None:
        facebook_enabled = False
        return HttpResponseRedirect("/")
    else:
        if fb_check == 'on':
            facebook_enabled = True
        else:
            facebook_enabled = False

    if facebook_account.is_authorized():
        return HttpResponseRedirect("/")

    facebook_auth_url = facebook_account.get_auth_url()
    return HttpResponseRedirect(facebook_auth_url)


def facebook_login_success(request):
    """Post login handler:
            if login was sucessful - save returned code, 
            and then get access token 
    """
    global facebook_enabled
    code = request.GET.get('code')
    if code is None:
        return HttpResponseForbidden(
                "Facebook login failed, Return code = None ")

    facebook_account.set_auth_code(code)
    facebook_account.request_access_token()

    facebook_enabled = True
    return HttpResponseRedirect("/")


def twitter_login(request):
    """Handle Twitter login status (On/Off checkbox)
       Authorize via twitter if first request.             
    """
    global twitter_enabled

    tw_check = request.GET.get('twitter_checkbox')
    print "tw_check = %s" % tw_check
    if tw_check is None:
        twitter_enabled = False
        return HttpResponseRedirect("/")
    else:
        if tw_check == 'on':
            twitter_enabled = True
        else:
            twitter_enabled = False

    if twitter_account.is_authorized():
        return HttpResponseRedirect("/")
    else:
        res, twitter_auth_url = twitter_account.get_auth_url()
        if res:
            return HttpResponseRedirect(twitter_auth_url)
        else:
            return HttpResponseBadRequest(
                    'Invalid respond from Twitter requesting temp token: %s' % 
                    twitter_auth_url)


def twitter_login_success(request):
    """Post login handler:
            if login was sucessful - save verifier, 
            and then get access token 
    """
    global twitter_enabled

    twitter_oauth_verifier = request.GET.get('oauth_verifier')
    if twitter_oauth_verifier is None:
        return HttpResponseForbidden(
                    "Twitter oauth verification code request failed")

    twitter_account.set_oauth_verifier(twitter_oauth_verifier)

    error = twitter_account.request_access_token()
    if error is not None:
        return HttpResponseServerError(error)

    twitter_enabled = True
    return HttpResponseRedirect("/")
