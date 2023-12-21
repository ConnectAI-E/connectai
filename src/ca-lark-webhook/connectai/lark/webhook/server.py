import logging

from flask import Flask, jsonify, request

from connectai.lark.sdk import *


class LarkServer(object):
    def __init__(
        self, *bot, bots=list(), prefix="/api/feishu", host="0.0.0.0", port=8888
    ):
        self.bots = list(bot) + bots
        self.bots_map = {b.app_id: b for b in self.bots}
        self.prefix = prefix
        self.host = host
        self.port = port

    def get_app(self):
        app = Flask(__name__)

        def webhook_handler(app_id):
            bot = self.bots_map.get(app_id)
            if bot:
                result = bot.process_message(
                    {
                        "headers": {
                            key.lower(): value for key, value in request.headers.items()
                        },
                        "body": request.json,
                    }
                )
                if result:
                    return jsonify(result)
            return ""

        app.add_url_rule(
            f"{self.prefix}/<app_id>",
            "webhook_handler",
            webhook_handler,
            methods=["POST"],
        )
        return app

    def start(self, host=None, port=None):
        app = self.get_app()
        app.run(host=host or self.host, port=port or self.port)

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
        event_type=None,
        message_type=None,
    ):
        def decorate(method):
            # try create new bot from arguments
            if app_id and app_secret:
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
                2. gen new on_message, and filter by event_type or message_type
                3. if not match, call old_on_message
                """
                old_on_message = getattr(bot, "on_message")

                def on_message(data, *args, **kwargs):
                    if "header" in data:
                        if event_type and event_type == data["header"]["event_type"]:
                            return method(
                                bot,
                                data["header"]["event_id"],
                                data["event"],
                                *args,
                                **kwargs,
                            )
                        elif (
                            not event_type
                            and data["header"]["event_type"] == "im.message.receive_v1"
                        ):
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
