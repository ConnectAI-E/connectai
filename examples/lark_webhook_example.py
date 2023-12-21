import os

from dotenv import find_dotenv, load_dotenv

from connectai.lark.sdk import FeishuStickerMessage
from connectai.lark.webhook import LarkServer

load_dotenv(find_dotenv())

app = LarkServer()


@app.on_bot_message(
    app_id=os.environ.get("APP_ID"),
    app_secret=os.environ.get("APP_SECRET"),
    encrypt_key=os.environ.get("ENCRYPT_KEY"),
    verification_token=os.environ.get("VERIFICATION_TOKEN"),
    message_type="text",
)
def on_text_message(bot, message_id, content, *args, **kwargs):
    text = content["text"]
    print("bot", bot)
    bot.reply_text(message_id, "reply: " + text)


@app.on_bot_message(app_id=os.environ.get("APP_ID"), message_type="sticker")
def on_sticker_message(bot, message_id, content, *args, **kwargs):
    # reply sticker
    file_key = content["file_key"]
    bot.reply(message_id, FeishuStickerMessage(file_key))


@app.on_bot_message(
    app_id=os.environ.get("APP_ID"), event_type="im.message.reaction.created_v1"
)
def on_reaction_created(bot, event_id, event, *args, **kwargs):
    # reply sticker
    print("event_id", event_id, event)


app.start()
