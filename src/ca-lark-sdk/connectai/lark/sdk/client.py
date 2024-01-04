import base64
import hashlib
import json
import logging
import sys
from functools import cached_property
from time import time

import httpx
from Crypto.Cipher import AES

LARK_HOST = "https://open.feishu.cn"


class AESCipher(object):
    def __init__(self, key):
        self.bs = AES.block_size
        self.key = hashlib.sha256(AESCipher.str_to_bytes(key)).digest()

    @staticmethod
    def str_to_bytes(data):
        u_type = type(b"".decode("utf8"))
        if isinstance(data, u_type):
            return data.encode("utf8")
        return data

    @staticmethod
    def _unpad(s):
        return s[: -ord(s[len(s) - 1 :])]

    def decrypt(self, enc):
        iv = enc[: AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size :]))

    def decrypt_string(self, enc):
        enc = base64.b64decode(enc)
        return self.decrypt(enc).decode("utf8")


class Bot(object):
    def __init__(
        self,
        app_id=None,
        app_secret=None,
        verification_token=None,
        encrypt_key=None,
        host=LARK_HOST,
        storage=None,
    ):
        self.app_id = app_id
        self.app_secret = app_secret
        self.encrypt_key = encrypt_key
        self.verification_token = verification_token
        self.host = host
        self.storage = storage

    def _access_token_by_name(self, name):
        # https://open.feishu.cn/document/ukTMukTMukTM/ukDNz4SO0MjL5QzM/auth-v3/auth/tenant_access_token_internal
        url = f"{self.host}/open-apis/auth/v3/{name}/internal"
        result = self.post(
            url,
            json={
                "app_id": self.app_id,
                "app_secret": self.app_secret,
            },
        ).json()
        if name not in result:
            raise Exception(f"get {name} error")
        return result[name], result["expire"] + time()

    @cached_property
    def _tenant_access_token(self):
        return self._access_token_by_name("tenant_access_token")

    @cached_property
    def _app_access_token(self):
        return self._access_token_by_name("app_access_token")

    def access_token_by_name(self, name):
        key = f"{name}:{self.app_id}"
        try:
            token, expired = json.loads(self.storage.get(key))
        except Exception as e:
            logging.debug("error to get %r from storage %r", name, e)
            token, expired = getattr(self, f"_{name}")
            try:
                self.storage.set(key, json.dumps([token, expired]))
            except Exception as e:
                logging.debug("error to save %r to storage %r", name, e)
        if not token or expired < time():
            # retry get_tenant_access_token
            delattr(self, f"_{name}")
            token, expired = getattr(self, f"_{name}")
            try:
                self.storage.set(key, json.dumps([token, expired]))
            except Exception as e:
                logging.debug("error to save %r to storage %r", name, e)
        return token

    @property
    def tenant_access_token(self):
        return self.access_token_by_name("tenant_access_token")

    @property
    def app_access_token(self):
        return self.access_token_by_name("app_access_token")

    def request(self, method, url, headers=dict(), **kwargs):
        if "access_token" not in url and "Authorization" not in headers:
            headers["Authorization"] = "Bearer {}".format(self.tenant_access_token)
        return httpx.request(method, url, headers=headers, **kwargs)

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)

    def url_verification(self, message):
        challenge = message["body"]["challenge"]
        logging.debug("url_verification %r", challenge)
        return {"challenge": challenge}

    def _validate(self, encrypt_key, message):
        if (
            not encrypt_key
            or not message["headers"].get("x-lark-signature")
            or not message["body"].get("header")
        ):
            return
        timestamp = message["headers"]["x-lark-request-timestamp"]
        nonce = message["headers"]["x-lark-request-nonce"]
        signature = message["headers"]["x-lark-signature"]
        body = json.dumps(message["body"], separators=(",", ":")).encode()
        bytes_b = (timestamp + nonce + encrypt_key).encode("utf-8") + body
        hexdigest = hashlib.sha256(bytes_b).hexdigest()
        if signature != hexdigest:
            raise Exception("invalide signature")

    def process_message(self, message):
        # TODO validate message
        self._validate(self.encrypt_key, message)

        if "encrypt" in message["body"]:
            data = self._decrypt_data(self.encrypt_key, message["body"]["encrypt"])
        else:
            data = message["body"]

        if data.get("type") == "url_verification":
            if self.verification_token and "token" in data:
                if self.verification_token != data["token"]:
                    raise Exception("invalide token")
            return self.url_verification({"body": data})
        return self.on_message(data, message)

    def _decrypt_data(self, encrypt_key, encrypt_data):
        cipher = AESCipher(encrypt_key)
        return json.loads(cipher.decrypt_string(encrypt_data))

    def send(self, receive_id, content, msg_type="text", receive_id_type="open_id"):
        # https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create
        url = f"{self.host}/open-apis/im/v1/messages?receive_id_type={receive_id_type}"
        data = {
            "receive_id": receive_id,
            "content": json.dumps(content),
            "msg_type": getattr(content, "msg_type")
            if hasattr(content, "msg_type")
            else msg_type,
        }
        return self.post(url, json=data)

    def update(self, message_id, content):
        # https://open.feishu.cn/open-apis/im/v1/messages/:message_id
        url = f"{self.host}/open-apis/im/v1/messages/{message_id}"
        body = {"content": json.dumps(content)}
        return self.request("PATCH", url, json=body)

    def reply(self, message_id, content, msg_type="text"):
        # https://open.feishu.cn/document/server-docs/im-v1/message/reply
        url = f"{self.host}/open-apis/im/v1/messages/{message_id}/reply"
        data = {
            "content": json.dumps(content),
            "msg_type": getattr(content, "msg_type")
            if hasattr(content, "msg_type")
            else msg_type,
        }
        return self.post(url, json=data)

    def reply_text(self, message_id, text):
        return self.reply(message_id, {"text": text}, msg_type="text")

    def send_text(self, receive_id, text, receive_id_type="open_id"):
        return self.send(
            receive_id, {"text": text}, receive_id_type=receive_id_type, msg_type="text"
        )

    def send_card(self, receive_id, content, receive_id_type="open_id"):
        return self.send(
            receive_id, content, receive_id_type=receive_id_type, msg_type="interactive"
        )

    def reply_card(self, message_id, content):
        return self.reply(message_id, content, msg_type="interactive")

    def update_card(self, message_id, content):
        return self.update(message_id, content)

    def on_message(self, data, *args, **kwargs):
        pass


class MarketBot(Bot):
    tenant_key = ""  # set before get tenant_access_token

    @cached_property
    def _app_access_token(self):
        # https://open.feishu.cn/document/server-docs/authentication-management/access-token/app_access_token
        url = f"{self.host}/open-apis/auth/v3/app_access_token"
        result = self.post(
            url,
            json={
                "app_id": self.app_id,
                "app_secret": self.app_secret,
                "app_ticket": self.storage.get(f"app_ticket:{self.app_id}"),
            },
        ).json()
        if "app_access_token" not in result:
            raise Exception("get app_access_token error")
        return result["app_access_token"], result["expire"] + time()

    @cached_property
    def _tenant_access_token(self):
        # https://open.feishu.cn/document/server-docs/authentication-management/access-token/tenant_access_token
        url = f"{self.host}/open-apis/auth/v3/tenant_access_token"
        result = self.post(
            url,
            json={
                "app_access_token": self.app_access_token,
                "tenant_key": self.tenant_key,
            },
        ).json()
        if "tenant_access_token" not in result:
            raise Exception("get tenant_access_token error")
        return result["tenant_access_token"], result["expire"] + time()

    def on_message(self, data, *args, **kwargs):
        if (
            "event_callback" == data.get("type")
            and "app_ticket" == data["event"]["type"]
        ):
            app_id = data["event"]["app_id"]
            app_ticket = data["event"]["app_ticket"]
            self.storage.set(f"app_ticket:{app_id}", app_ticket)
            return
