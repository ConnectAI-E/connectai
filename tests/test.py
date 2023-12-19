import connectai as ca
from connectai import *


def reply_text2(message):
    print("reply_text", message)
    # 这里可以利用contextvar拿到当前对应的message_ctx里面的数据
    print(
        "reply_text current_bot", current_bot, message_ctx.app_id, message_ctx.message
    )
    print("reply_text ", message.event.message.content.text)
    return "reply_text2 " + message.event.message.content.text


with ca.MessageBroker() as broker:
    # ca.NoopEventHandler('app1')
    # ca.FeishuCallbackHandler()  # 这个handler是集中所有的都走这边，所以不需要app_id
    ca.WSFeishuWebsocketHandler()  # 使用wslarkbot走转发逻辑，无需公网IP
    with ca.FeishuChatBot(
        app_id="cli_a5c9305ede38500d", app_secret="", encrypt_key=""
    ) as bot:
        # 支持一个event多个回调函数
        bot.send_text(reply_text2)
        pass
    with ca.FeishuChatBot(app_id="app2") as bot:
        pass


if __name__ == "__main__":
    broker.launch()
