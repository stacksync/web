
from django.contrib.auth.backends import ModelBackend
from models import CustomUser, CustomUserManager
import json
import requests
import datetime
import urllib
from requests_oauthlib import OAuth1
from urlparse import parse_qs
from django.conf import settings





# oauth = OAuth1Session(client_key="b3af4e669daf880fb16563e6f36051b105188d413", client_secret="c168e65c18d75b35d8999b534a3776cf")
# fetch_response = oauth.fetch_request_token(STACKSYNC_REQUEST_TOKEN_ENDPOINT)
#
# resource_owner_key = fetch_response.get('oauth_token')
# resource_owner_secret = fetch_response.get('oauth_token_secret')
#
# authorization_url = oauth.authorization_url(STACKSYNC_ACCESS_TOKEN_ENDPOINT)
# 
# 
class myBackend(ModelBackend):
 
    def authenticate(self, username=None, password=None,**kwargs):
        try:
            user = CustomUser.objects.get(username=username)

        except CustomUser.DoesNotExist:
            user = CustomUser(username=username, password=password)
            user.save()
            
        return user
#    