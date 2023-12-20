import os

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

import connectai as ca
from connectai import *
from connectai.lark.sdk import *

load_dotenv(find_dotenv())


def reply_text2(message):
    client = OpenAI(
        # This is the default and can be omitted
        api_key=os.environ.get("OPENAI_API_KEY"),
        base_url=os.environ.get("OPENAI_API_BASE"),
    )
    result = ""
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message.content.text}],
        stream=True,
    )
    for chunk in stream:
        token = chunk.choices[0].delta.content or ""
        result = result + token
        logging.info("new token %r", token)
        yield token

    return result


with ca.MessageBroker() as broker:
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
                FeishuMessageDiv("openai stream new token"),
                FeishuMessageHr(),
                FeishuMessageDiv(new_token),
                FeishuMessageHr(),
                FeishuMessageDiv("openai stream result"),
                FeishuMessageHr(),
                FeishuMessageDiv("".join(tokens)),
            )
        )
        bot.on_result(
            lambda result: FeishuMessageCard(
                FeishuMessageDiv("openai result"),
                FeishuMessageHr(),
                FeishuMessageDiv(result),
            )
        )
        pass


if __name__ == "__main__":
    broker.launch()
