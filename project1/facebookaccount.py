# -*- coding: utf-8 -*-
"""
      Wrapper for Twitter API
"""
import json
import urllib2
import datetime
import calendar

from pyfb import Pyfb

from project1.settings import FACEBOOK_APP_ID
from project1.settings import FACEBOOK_APP_SECRET
from project1.settings import FACEBOOK_REDIRECT_URL


FB_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S+0000'
FB_POST_URL = "https://www.facebook.com/%s/posts/%s"

def to_timestamp(fb_date):
    """Convert FB date to unix timestamp"""
    date = datetime.datetime.strptime(fb_date, FB_DATE_FORMAT)
    date_utc = date.utctimetuple()
    return calendar.timegm(date_utc)

def to_ctime(fb_date):
    """Convert FB date to ctime"""
    date = datetime.datetime.strptime(fb_date, FB_DATE_FORMAT)
    return date.ctime()


class FacebookAccount():
    """Wrapper for facebook API"""
    
    def __init__(self):
        self.user = None
        self._user_id = None
        self._access_token = None
        self._api = Pyfb(FACEBOOK_APP_ID)
        self._auth_code = None

    def is_authorized(self):
        """Check if authorized via FB"""
        if self._access_token is None:
            return False
        return True

    def _load_user_info(self):
        """Get out user info"""
        fb_user = self._api.get_myself()
        if fb_user is None:
            return False
        self.user = fb_user.name
        self._user_id = str(fb_user.id)
        return True

    def get_auth_url(self):
        """Return URL for authorization"""
        url = self._api.get_auth_code_url(redirect_uri=FACEBOOK_REDIRECT_URL)
        return url

    def set_auth_code(self, code):
        """Save auth. code returned from FB in case of sucessfull login"""
        self._auth_code = code

    def request_access_token(self):
        """Request access token from FB"""
        self._access_token = self._api.get_access_token(
                                        FACEBOOK_APP_SECRET, 
                                        self._auth_code, 
                                        redirect_uri=FACEBOOK_REDIRECT_URL)
        print "FB access token: %s" % self._access_token

#    def get_extended_at(self, short_lived_access_token):
#        """Get long time lived access token from short lived."""
#        from facepy.utils import get_extended_access_token
#        long_lived_access_token, expires_at = get_extended_access_token(
#            short_lived_access_token,
#            FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
#        return long_lived_access_token

    def load_messages(self, messages):
        """Load Messages from Twitter"""
        if not self.is_authorized(): 
            return False
        if self.user is None:
            if not self._load_user_info():
                return False

        print "facebook_access_token=%s" % self._access_token
        url = 'https://graph.facebook.com/%s/posts?access_token=%s' % (
            self._user_id, self._access_token)
        req = urllib2.Request(url)

        try:
            response = urllib2.urlopen(req)
        except ValueError:
            print "Connection Error - Cannot Load data from facebook "
            return False

        page = response.read()
        fb_data = json.loads(page)
        # print  json.dumps(fb_data,indent=2)
        response.close()

        msg_count = 0
        for msg in fb_data['data']:
            text = '' # Text to be will be shown on page 
            if 'story' in msg:
                text = msg['story']
            if 'message' in msg:
                text = msg['message']

            record_key = str(to_timestamp(msg['created_time'])) + "f"
            record = {'account': "facebook",
                      'created': to_ctime(msg['created_time']),
                      'text': text}
                      
            # Additionally parse url if this is 'like'-message  
            if text.find(" likes") >= 0:
                pic_id = msg['id'][msg['id'].find("_") + 1:]
                record['description'] = FB_POST_URL % (
                                            self._user_id, pic_id)
                record['link'] = FB_POST_URL % (
                                            self._user_id, pic_id)

            if 'link' in msg:
                record['link'] = msg['link']

            if 'picture' in msg:
                record['picture'] = msg['picture']

            if 'name' in msg:
                record['name'] = msg['name']

            if 'description' in msg:
                record['description'] = msg['description']

            messages[record_key] = record
            msg_count = msg_count + 1
        print "Facebook : %i messages loaded." % msg_count

