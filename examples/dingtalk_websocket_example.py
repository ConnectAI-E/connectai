import os

from dotenv import find_dotenv, load_dotenv

from connectai.dingtalk.sdk import DingtalkTextMessage
from connectai.dingtalk.websocket import Client

load_dotenv(find_dotenv())

client = Client()


@client.on_bot_message(
    app_id=os.environ.get("DAPP_ID"),
    app_secret=os.environ.get("DAPP_SECRET"),
    agent_id=os.environ.get("AGENT_ID"),
    msgtype="text",
)
def on_text_message(bot, sessionWebhook, content, *args, **kwargs):
    text = content["content"]
    print("reply: ", text)
    bot.reply(sessionWebhook, DingtalkTextMessage("reply: " + text))


client.start()
