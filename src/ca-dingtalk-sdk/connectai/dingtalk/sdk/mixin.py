import json
import logging

from .client import DING_HOST, Bot


class BotMessageDecorateMixin(object):
    def get_bot(self, app_id):
        return self.bots_map.get(app_id)

    def add_bot(self, bot):
        if bot.app_id not in self.bots_map:
            self.bots_map[bot.app_id] = bot
            self.bots.append(bot)
        else:
            logging.warning("duplicate bot %r", bot.app_id)

    def on_bot_message(self, msgtype=None, bot=None, **kwargs):
        def decorate(method):
            # try create new bot from arguments
            if bot:
                self.add_bot(bot)
            if kwargs.get("app_id") and kwargs.get("app_secret"):
                self.add_bot(Bot(**kwargs))

            """
            1. get old on_message
            2. gen new on_message, and filter by event_type or message_type
            3. if not match, call old_on_message
            """
            old_on_message = getattr(Bot, "on_message")

            def on_message(_bot, data, *args, **kwargs):
                real_msgtype = data["msgtype"]
                if msgtype and msgtype != real_msgtype:
                    logging.warning("msgtype (%r) not match!", real_msgtype)
                else:
                    return method(
                        _bot,
                        data["sessionWebhook"],
                        data[real_msgtype],
                        data,
                        *args,
                        **kwargs
                    )
                return old_on_message(_bot, data, *args, **kwargs)

            setattr(Bot, "on_message", on_message)
            return method

        return decorate
