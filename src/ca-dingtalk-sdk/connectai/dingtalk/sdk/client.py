import base64
import hashlib
import hmac
import json
from functools import cached_property
from time import time

import httpx

DING_HOST = "https://api.dingtalk.com"


class Bot(object):
    def __init__(
        self,
        app_id=None,
        app_secret=None,
        agent_id=None,
        host=DING_HOST,
    ):
        self.app_id = app_id
        self.app_secret = app_secret
        self.agent_id = agent_id
        self.host = host

    @cached_property
    def _access_token(self):
        # https://open.dingtalk.com/document/orgapp/obtain-the-access_token-of-an-internal-app?spm=ding_open_doc.document.0.0.66fe4a97E7FClg
        url = f"{self.host}/v1.0/oauth2/accessToken"
        result = httpx.post(
            url,
            json={
                "appKey": self.app_id,
                "appSecret": self.app_secret,
            },
        ).json()
        if "accessToken" not in result:
            raise Exception("get accessToken error")
        return result["accessToken"], result["expireIn"] + time()

    @property
    def access_token(self):
        token, expired = self._access_token
        if not token or expired < time():
            # retry get_access_token
            del self._access_token
            token, expired = self._access_token
        return token

    def request(self, method, url, headers=dict(), **kwargs):
        headers["x-acs-dingtalk-access-token"] = self.access_token
        return httpx.request(method, url, headers=headers, **kwargs)

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)

    def calc_sign(self, timestamp):
        msg = "{}\n{}".format(timestamp, self.app_secret).encode()
        h = hmac.new(self.app_secret.encode(), msg=msg, digestmod=hashlib.sha256)
        return base64.b64encode(h.digest()).decode()

    def validate_sign(self, timestamp, sign):
        return sign == self.calc_sign(timestamp)

    def process_message(self, message):
        # TODO validate message
        self.validate_sign(message["headers"]["timestamp"], message["headers"]["sign"])
        self.on_message(message["body"], message)

    def reply(self, sessionWebhook, content):
        return httpx.post(sessionWebhook, json=content).json()

    def on_message(self, data, *args, **kwargs):
        pass
