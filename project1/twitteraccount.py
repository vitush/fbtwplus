# -*- coding: utf-8 -*-
"""

    TwitterAccount - Wrapper for Twitter API.
    
        Authorization process:
            1) Use get_auth_url() to get Authorization URL on Twitter.
            2) Load auth. URL (in browser. etc) to get  oauth-verifier
            3) save returned  oauth-verifier using set_oauth_verifier()
            4) request access-token using request_access_token()
        
        Usage: 
            1) use load_messages() to load messages/posts from Twitter 
                       

"""
import oauth2 as oauth
from urlparse import parse_qsl
import datetime

import twitter

from project1.settings import TWITTER_CUSTOMER_KEY, TWITTER_CUSTOMER_SECRET
from project1.settings import TWITTER_AUTHORIZATION_URL
from project1.settings import TWITTER_REQUEST_TOKEN_URL
from project1.settings import TWITTER_ACCESS_TOKEN_URL

class TwitterAccount():
    """Wrapper for twitter API"""

    def __init__(self):
        self._api = None
        self._oauth_token = None
        self._access_token_key = None
        self._access_token_secret = None
        self._auth_url = None
        self._oauth_verifier = None
        self._oauth_consumer = oauth.Consumer(
            key=TWITTER_CUSTOMER_KEY, secret=TWITTER_CUSTOMER_SECRET)
        self.access_token = None
        self.user = None

    def get_auth_url(self):
        """Get auth. URL to connect to twitter"""
        oauth_client = oauth.Client(self._oauth_consumer)
        resp, content = oauth_client.request(TWITTER_REQUEST_TOKEN_URL, 'GET')

        if resp['status'] != '200':
            error = 'Invalid respond from Twitter while \
                     requesting temporary token: %s' % resp['status']
            return False, error

        request_token = dict(parse_qsl(content))
        self._oauth_token = oauth.Token(
            request_token['oauth_token'], request_token['oauth_token_secret'])
        self._auth_url = "%s?oauth_token=%s" % (
            TWITTER_AUTHORIZATION_URL, request_token['oauth_token'])

        return True, self._auth_url

    def _load_user_info(self):
        """Load user information"""
        if self._api is None:
            return False
        try:
            tw_user = self._api.VerifyCredentials()
        except ValueError:
            print "Twitter - Rate limit exceeded. Ingnoring "
            return False
        self.user = tw_user.screen_name
        return True

    def set_oauth_verifier(self, twitter_oauth_verifier):
        """Save oauth. verifier returned from Twitter"""
        self._oauth_token.set_verifier(twitter_oauth_verifier)

    def request_access_token(self):
        """Request access token from Twitter"""
        oauth_client = oauth.Client(self._oauth_consumer, self._oauth_token)
        body = 'oauth_callback=oob&oauth_verifier=%s' % self._oauth_verifier
        resp, content = oauth_client.request(
                            TWITTER_ACCESS_TOKEN_URL, 
                            method='POST', 
                            body=body)
        self._oauth_token = dict(parse_qsl(content))

        if resp['status'] != '200':
            return 'The request for access token failed: %s' % resp['status']

        self._access_token_key = self._oauth_token['oauth_token']
        self._access_token_secret = self._oauth_token['oauth_token_secret']
        self._api = twitter.Api(consumer_key=TWITTER_CUSTOMER_KEY,
                                 consumer_secret=TWITTER_CUSTOMER_SECRET,
                                 access_token_key=self._access_token_key,
                                 access_token_secret=self._access_token_secret)

        print ('Twitter Access Token Key: %s' % self._access_token_key)
        print ('Twitter Access Token Secret: %s' % self._access_token_secret)

        return None

    def is_authorized(self):
        """Check if already authorized via Twitter"""
        if self._api is None:
            return False
        return True

    def load_messages(self, messages):
        """Load Messages from Twitter"""
        if not self.is_authorized():
            return False
        if self.user is None:
            if not self._load_user_info():
                return False
        
        # Load and parse messages/posts 
        msg_count = 0
        try:
            statuses = self._api.GetUserTimeline(self.user)
            for status in statuses:
                created = datetime.datetime.fromtimestamp(
                    status.GetCreatedAtInSeconds())

                record_key = str(status.GetCreatedAtInSeconds()) + "t"
                record = {'account': "twitter",
                          'created': created.ctime(),
                          'text': status.text}

                if 'urls' in status.AsDict():
                    for val in status.AsDict()['urls'].values():
                        record['picture'] = val
                        record['link'] = val
                        break

                messages[record_key] = record
                msg_count = msg_count + 1

            print "Twitter %i messages loaded." % msg_count
        except ValueError:
            print "Twitter - Rate limit exceeded. Ingnoring "
        return True
