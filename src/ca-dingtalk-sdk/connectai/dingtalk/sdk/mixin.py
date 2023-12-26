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

    def on_bot_message(
        self,
        app_id=None,
        app_secret=None,
        agent_id=None,
        host=DING_HOST,
        msgtype=None,
    ):
        def decorate(method):
            # try create new bot from arguments
            if app_id and app_secret:
                bot = Bot(
                    app_id=app_id,
                    app_secret=app_secret,
                    agent_id=agent_id,
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
                    real_msgtype = data["msgtype"]
                    if msgtype and msgtype != real_msgtype:
                        logging.warning("msgtype (%r) not match!", real_msgtype)
                    else:
                        return method(
                            bot,
                            data["sessionWebhook"],
                            data[real_msgtype],
                            *args,
                            **kwargs
                        )
                    return old_on_message(data, *args, **kwargs)

                setattr(bot, "on_message", on_message)
            return method

        return decorate
