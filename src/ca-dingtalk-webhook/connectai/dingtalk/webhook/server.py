import logging

from flask import Blueprint, Flask, jsonify, request

from connectai.dingtalk.sdk import *
from connectai.dingtalk.sdk.mixin import BotMessageDecorateMixin


class DingtalkServer(BotMessageDecorateMixin):
    def __init__(
        self, *bot, bots=None, prefix="/api/dingtalk", host="0.0.0.0", port=8888
    ):
        self.bots = list(bot) + (bots or list())
        self.bots_map = {b.app_id: b for b in self.bots}
        self.prefix = prefix
        self.host = host
        self.port = port

    def get_blueprint(self):
        bp = Blueprint("dingtalk-webhook", __name__)

        def webhook_handler(app_id):
            bot = self.get_bot(app_id)
            if request.method == "POST" and bot:
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

        bp.add_url_rule(
            f"{self.prefix}/<app_id>",
            "webhook_handler",
            webhook_handler,
            methods=["GET", "POST"],
        )
        return bp

    def get_app(self):
        app = Flask(__name__)
        app.register_blueprint(self.get_blueprint())
        return app

    def start(self, host=None, port=None):
        app = self.get_app()
        app.run(host=host or self.host, port=port or self.port)
