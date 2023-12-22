import os

from dotenv import find_dotenv, load_dotenv

from connectai.dingtalk.sdk import DingtalkTextMessage
from connectai.dingtalk.webhook import DingtalkServer

load_dotenv(find_dotenv())

app = DingtalkServer()


@app.on_bot_message(
    app_id=os.environ.get("DAPP_ID"),
    app_secret=os.environ.get("DAPP_SECRET"),
    agent_id=os.environ.get("AGENT_ID"),
    msgtype="text",
)
def on_text_message(bot, sessionWebhook, content, *args, **kwargs):
    text = content["content"]
    bot.reply(sessionWebhook, DingtalkTextMessage("reply: " + text))


app.start()
