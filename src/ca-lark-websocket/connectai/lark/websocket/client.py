import base64
import json
import logging
import sys

import httpx
import websocket

from connectai.lark.sdk import *

WS_LARK_PROXY_SERVER = "feishu.forkway.cn"
WS_LARK_PROXY_PROTOCOL = "https"


class Client(object):
    def __init__(
        self,
        *bot,
        bots=list(),
        server=WS_LARK_PROXY_SERVER,
        protocol=WS_LARK_PROXY_PROTOCOL,
        org_name="",
        org_passwd="",
    ):
        self.bots = list(bot) + bots
        self.bots_map = {b.app_id: b for b in self.bots}
        self.server = server
        self.protocol = protocol
        self.ws_protocol = "wss" if protocol == "https" else "ws"
        self.org_name = org_name
        self.org_passwd = org_passwd
        self.is_org = org_name and "org_" in org_name

    def get_server_url(self, *channels, ws=False):
        return "{}://{}/sub/{}".format(
            self.ws_protocol if ws else self.protocol,
            self.server,
            self.org_name if ws and self.is_org else ",".join(channels),
        )

    @property
    def header(self):
        if self.org_name and self.org_passwd:
            auth = base64.b64encode(
                f"{self.org_name}:{self.org_passwd}".encode()
            ).decode()
            return dict(Authorization=f"Basic {auth}")
        return dict()

    def start(self, debug=False):
        if debug:
            websocket.enableTrace(True)
        proxy_url = self.get_server_url(*[b.app_id for b in self.bots], ws=True)
        hooks = "\n".join(
            [
                self.protocol
                + "://"
                + self.server
                + "/"
                + (self.org_name if self.is_org else "hook")
                + "/"
                + b.app_id
                for b in self.bots
            ]
        )
        print(f"hooks: \n{hooks}", file=sys.stderr)

        def run_forever(*args):
            app.run_forever()

        app = websocket.WebSocketApp(
            proxy_url,
            header=self.header,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=run_forever,
        )
        run_forever()

    def _on_message(self, wsapp, message):
        try:
            message = json.loads(message)
            if "headers" not in message:
                logging.debug("no headers in message %r", message)
                return
            app_id = message["headers"]["x-app-id"]
            bot = self.bots_map.get(app_id)
            if bot:
                result = bot.process_message(message)
                if result:
                    request_id = message["headers"]["x-request-id"]
                    url = self.get_server_url(request_id)
                    res = httpx.post(url, json=result)
                    logging.debug("res %r", res.text)
        except Exception as e:
            logging.exception(e)

    def _on_error(self, wsapp, error):
        logging.error("error %r", error)
        if isinstance(error, KeyboardInterrupt):
            sys.exit()

    def add_bot(self, bot):
        if bot.app_id not in self.bots_map:
            self.bots_map[bot.app_id] = bot
            self.bots.append(bot)
        else:
            logging.warning("duplicate bot %r", bot.app_id)

    def on_bot_message(
        self,
        app_id=None,
        app_secret=None,
        encrypt_key=None,
        verification_token=None,
        host=LARK_HOST,
        message_type=None,
    ):
        def decorate(method):
            # try create new bot from arguments
            if app_id:
                bot = Bot(
                    app_id=app_id,
                    app_secret=app_secret,
                    encrypt_key=encrypt_key,
                    verification_token=verification_token,
                    host=host,
                )
                self.add_bot(bot)

            bot = self.bots_map.get(app_id)
            if bot:
                """
                1. get old on_message
                2. gen new on_message, and filter by message_type
                3. if not match, call old_on_message
                """
                old_on_message = getattr(bot, "on_message")

                def on_message(data, *args, **kwargs):
                    if "header" in data:
                        if data["header"]["event_type"] == "im.message.receive_v1":
                            real_message_type = data["event"]["message"]["message_type"]
                            if message_type and message_type != real_message_type:
                                logging.warning(
                                    "message_type (%r) not match!", real_message_type
                                )
                            else:
                                message_id = data["event"]["message"]["message_id"]
                                content = json.loads(
                                    data["event"]["message"]["content"]
                                )
                                return method(bot, message_id, content, *args, **kwargs)
                    return old_on_message(data, *args, **kwargs)

                setattr(bot, "on_message", on_message)
            return method

        return decorate
