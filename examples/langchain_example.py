import os
from typing import Annotated, Callable, Generator

from dotenv import find_dotenv, load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain_core.language_models import BaseLLM
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import GoogleGenerativeAI

import connectai as ca
from connectai.globals import broker_ctx
from connectai.lark.sdk.message import FeishuMessageCard, FeishuMessageDiv
from connectai.message import Message

load_dotenv(find_dotenv(), override=True)


def speed_limit(limit: int = 15) -> Callable:
    def decorate(fn: Callable):
        def wrapper(*args, **kwargs):
            results = fn(*args, **kwargs)
            if not isinstance(results, Generator):
                return results

            temp_result = ""
            send_result = ""

            for result in fn(*args, **kwargs):
                temp_result += result
                if len(temp_result) > limit:
                    send_result += temp_result
                    temp_result = ""
                    yield send_result

                yield ""

            yield send_result + temp_result

        return wrapper

    return decorate


class langchainChatBaseBot(object):
    app_id: str
    app_secret: str
    encrypt_key: str
    streaming: bool
    chat: BaseLLM
    bot: ca.FeishuChatBot

    def __init__(
        self,
        app_id="",
        app_secret="",
        encrypt_key="",
        streaming=False,
    ) -> None:
        self.app_id = app_id
        self.app_secret = app_secret
        self.encrypt_key = encrypt_key
        self.streaming = streaming
        self.chat: Annotated[BaseLLM, BaseChatModel] = None
        self.bot = None

    @speed_limit(15)
    def reply_text(self, message: Message) -> Annotated[Generator, str]:
        text = message.content.text

        messages = []
        messages.append(HumanMessage(content=text))

        # 调用 LLM/ChatModel
        if self.streaming:
            for chunk in self.chat.stream(messages):
                if isinstance(chunk, str):
                    yield chunk
                else:
                    yield chunk.content
        else:
            return self.chat.invoke(messages)

    def run(self):
        if self.chat is None:
            raise Exception("chat is None")

        current_broker = broker_ctx.broker
        self.bot = ca.FeishuChatBot(
            app_id=self.app_id,
            app_secret=self.app_secret,
            encrypt_key=self.encrypt_key,
        )
        self.bot.on_text(self.reply_text)
        self.bot.on_new_token(
            lambda new_token, tokens: FeishuMessageCard(
                FeishuMessageDiv(new_token),
            )
        )
        self.bot.on_result(lambda result: FeishuMessageCard(FeishuMessageDiv(result)))

        current_broker.register_bot(self.bot)


class OpenAIChatBot(langchainChatBaseBot):
    def __init__(
        self,
        app_id=os.environ.get("APP_ID"),
        app_secret=os.environ.get("APP_SECRET"),
        encrypt_key=os.environ.get("ENCRYPT_KEY"),
        streaming=False,
    ) -> None:
        super().__init__(app_id, app_secret, encrypt_key, streaming)
        self.chat = ChatOpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url=os.environ.get("OPENAI_BASE_URL"),
            model="gpt-3.5-turbo",
        )


class GeminiChatBot(langchainChatBaseBot):
    def __init__(
        self,
        app_id=os.environ.get("APP_ID"),
        app_secret=os.environ.get("APP_SECRET"),
        encrypt_key=os.environ.get("ENCRYPT_KEY"),
        streaming=False,
    ) -> None:
        super().__init__(app_id, app_secret, encrypt_key, streaming)
        self.chat = GoogleGenerativeAI(
            model="gemini-pro", google_api_key=os.environ.get("GOOGLE_API_KEY")
        )

    def run(self):
        try:
            super().run()
        except Exception as e:
            print(e)


class FeishuAPP(object):
    bots: list[langchainChatBaseBot]

    def __init__(self, bots: list[langchainChatBaseBot]) -> None:
        self.bots = bots

    def add_bot(self, bot: langchainChatBaseBot):
        self.bots.append(bot)

    def run(self):
        with ca.MessageBroker() as broker:
            ca.WSFeishuWebsocketReceiver()
            for bot in self.bots:
                bot.run()

            print(os.environ.get("APP_ID"))
            broker.launch()


if __name__ == "__main__":
    app = FeishuAPP(
        bots=[
            # OpenAIChatBot(),
            GeminiChatBot(streaming=True),
        ]
    )

    # app.add_bot(OpenAIChatBot())
    # app.add_bot(GeminiChatBot())

    app.run()
