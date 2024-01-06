import json
import logging

from .client import LARK_HOST, Bot, MarketBot


class BotMessageDecorateMixin(object):
    def get_bot(self, app_id):
        return self.bots_map.get(app_id)

    def add_bot(self, bot):
        if bot.app_id not in self.bots_map:
            self.bots_map[bot.app_id] = bot
            self.bots.append(bot)
        else:
            logging.warning("duplicate bot %r", bot.app_id)

    def on_bot_event(
        self,
        event_type=None,
        app_type=None,  # internal/market
        bot=None,
        **kwargs,
    ):
        return self.on_bot_message(
            event_type=event_type,
            app_type=app_type,
            bot=bot,
            **kwargs,
        )

    def on_bot_message(
        self,
        message_type=None,
        event_type=None,
        app_type=None,  # internal/market
        bot=None,
        **kwargs,
    ):
        def decorate(method):
            # try create new bot from arguments
            if bot:
                self.add_bot(bot)
            cls = MarketBot if app_type == "market" else Bot
            if kwargs.get("app_id") and kwargs.get("app_secret"):
                self.add_bot(cls(**kwargs))

            """
            1. get old on_message
            2. gen new on_message, and filter by event_type or message_type
            3. if not match, call old_on_message
            """
            old_on_message = getattr(cls, "on_message")

            def on_message(_bot, data, *args, **kwargs):
                if "action" in data:
                    # card event
                    if event_type and event_type == "card:action":
                        return method(
                            _bot,
                            data["token"],
                            data,
                            *args,
                            **kwargs,
                        )
                elif "header" in data:
                    if "tenant_key" in data["header"] and isinstance(_bot, MarketBot):
                        _bot.tenant_key = data["header"]["tenant_key"]
                    if event_type and event_type == data["header"]["event_type"]:
                        return method(
                            _bot,
                            data["header"]["event_id"],
                            data["event"],
                            data,
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
                            content = json.loads(data["event"]["message"]["content"])
                            return method(
                                _bot, message_id, content, data, *args, **kwargs
                            )
                return old_on_message(_bot, data, *args, **kwargs)

            setattr(cls, "on_message", on_message)
            return method

        return decorate
