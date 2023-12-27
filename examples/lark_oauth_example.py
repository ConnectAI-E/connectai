import os

from dotenv import find_dotenv, load_dotenv

from connectai.lark.oauth import Server as OauthServer
from connectai.lark.sdk import MarketBot
from connectai.lark.webhook import LarkServer
from connectai.storage import ExpiredDictStorage

load_dotenv(find_dotenv())

hook = LarkServer()
oauth = OauthServer()

bot = MarketBot(
    app_id=os.environ.get("APP_ID"),
    app_secret=os.environ.get("APP_SECRET"),
    encrypt_key=os.environ.get("ENCRYPT_KEY"),
    verification_token=os.environ.get("VERIFICATION_TOKEN"),
    storage=ExpiredDictStorage(items={}),
)
hook.add_bot(bot)
oauth.add_bot(bot)


@hook.on_bot_message(
    app_id=os.environ.get("APP_ID"),
    app_secret=os.environ.get("APP_SECRET"),
    encrypt_key=os.environ.get("ENCRYPT_KEY"),
    verification_token=os.environ.get("VERIFICATION_TOKEN"),
    message_type="text",
)
def on_text_message(bot, message_id, content, *args, **kwargs):
    text = content["text"]
    print("reply_text", message_id, text)
    bot.reply_text(message_id, "reply: " + text)


@oauth.on_bot_event(
    app_id=os.environ.get("APP_ID"),
    app_secret=os.environ.get("APP_SECRET"),
    event_type="oauth:user_info",
)
def on_oauth_user_info(bot, event_id, user_info, *args, **kwargs):
    # oauth user_info
    print("oauth", user_info)


app = oauth.get_app()
app.register_blueprint(hook.get_blueprint())


if __name__ == "__main__":
    # gunicorn -w 1 -b :8888 "examples.lark_oauth_example:app"
    app.run(host="0.0.0.0", port=8888)
