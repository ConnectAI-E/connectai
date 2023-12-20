import os

from dotenv import find_dotenv, load_dotenv

import connectai as ca
from connectai import *
from connectai.lark.sdk import *

load_dotenv(find_dotenv())


def reply_text2(message):
    print("reply_text", message)
    # 这里可以利用contextvar拿到当前对应的message_ctx里面的数据
    # test from noopreceiver
    # yield FeishuMessageCard(
    #     FeishuMessageDiv('reply1'),
    #     FeishuMessageHr(),
    #     FeishuMessageDiv(message.raw.event.message.content.text)
    # )
    # yield FeishuMessageCard(
    #     FeishuMessageDiv('reply2'),
    #     FeishuMessageHr(),
    #     FeishuMessageDiv(message.raw.event.message.content.text)
    # )
    # # finally result
    # return FeishuMessageCard(
    #     FeishuMessageDiv('reply_result'),
    #     FeishuMessageHr(),
    #     FeishuMessageDiv(message.raw.event.message.content.text)
    # )
    yield "reply_text1 " + message.raw.event.message.content.text
    yield "reply_text2 " + message.raw.event.message.content.text
    # finally result
    return "reply_result " + message.raw.event.message.content.text


with ca.MessageBroker() as broker:
    # ca.NoopReceiver(os.environ.get("APP_ID"))
    # ca.NoopEventHandler('app1')
    # ca.FeishuWebhookReceiver()  # 这个handler是集中所有的都走这边，所以不需要app_id
    ca.WSFeishuWebsocketReceiver()  # 使用wslarkbot走转发逻辑，无需公网IP
    with ca.FeishuChatBot(
        app_id=os.environ.get("APP_ID"),
        app_secret=os.environ.get("APP_SECRET"),
        encrypt_key=os.environ.get("ENCRYPT_KEY"),
    ) as bot:
        # 支持一个event多个回调函数
        bot.on_text(reply_text2)
        # 支持通过on_new_token + on_result对消息进行处理，或者直接在reply_message函数直接返回对应的message
        bot.on_new_token(
            lambda new_token, tokens: FeishuMessageCard(
                FeishuMessageDiv("new_token"),
                FeishuMessageHr(),
                FeishuMessageDiv(new_token),
            )
        )
        bot.on_result(
            lambda result: FeishuMessageCard(
                FeishuMessageDiv("result"), FeishuMessageHr(), FeishuMessageDiv(result)
            )
        )
        pass


if __name__ == "__main__":
    broker.launch()