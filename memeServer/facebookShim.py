import requests
from urllib import urlencode
import json

from . import settings
from . import models

class FacebookShim():

    def get_user(self, auth_code):
        """Given an auth code, run through the Oauth flow and return a user object
        :param: auth_code: 
        :return: User id
        """
        payload = self._get("https://graph.facebook.com/me?access_token=" + auth_code)
        payload_dict = json.loads(payload)
        return {
            "name": payload_dict['name'],
            "user_id": payload_dict['id']
        }

    def _get(self, url):
        """
        Make Get Request
        :param url: Base URL
        :param params: Parameter argument specified as tuple of 2-tuples
        :return: the response body
        """
        r = requests.get(url)
        r.raise_for_status()
        return r.text
