import json
import logging
from enum import IntEnum, auto
from typing import Dict, Union

from connectai.lark.sdk import FeishuBaseMessage


class Message(Dict):
    def __getattribute__(self, name):
        if name in self:
            result = self[name]
            return self.__class__(**result) if isinstance(result, dict) else result
        return super().__getattribute__(name)


class FeishuEventMessage(Message):
    def __getattribute__(self, name):
        if (
            name in self
            and "message" == name
            and "content" in self[name]
            and isinstance(self[name]["content"], str)
        ):
            try:
                result = self[name]
                result["content"] = json.loads(result["content"])
                # remove @
                for mention in result.get("mentions", []):
                    result["content"]["text"] = result["content"]["text"].replace(
                        mention["key"] + " ", "    "
                    )
                # 移除@_all
                result["content"]["text"] = result["content"]["text"].replace(
                    "@_all ", ""
                )
            except Exception as e:
                logging.debug(e)
            return self.__class__(**result) if isinstance(result, dict) else result
        return super().__getattribute__(name)


class DingtalkEventMessage(Message):
    pass


class WeworkEventMessage(Message):
    pass


class MessageType(IntEnum):
    Unkown = 0
    # input or just send message
    Text = 100
    File = auto()
    Audio = auto()
    Media = auto()
    Sticker = auto()

    # send feishu interactive message
    Card = 109
    Interactive = 109

    # send dingtalk action card message
    # https://open.dingtalk.com/document/orgapp/receive-message
    ActionCard = 110
    FeedCard = auto()
    Picture = auto()
    Video = auto()
    Markdown = auto()
    RichText = auto()
    # send wework template card message
    TemplateCard = 120

    ReplyText = 200
    ReplyFile = auto()
    ReplyAudio = auto()
    ReplyMedia = auto()
    ReplySticker = auto()
    # feishu interactive message type
    ReplyCard = auto()
    UpdateCard = auto()

    # reply dingtalk action card message
    ReplyActionCard = 210
    ReplyFeedCard = auto()
    ReplyMarkdown = auto()
    # reply wework template card message
    ReplyTemplateCard = 220  # wework


class QueueMessage(Dict):
    """
    message type transfer in bot_queue and message_queue
    reqired attribute: type
    reqired attribute: content
    reqired attribute: raw
    optional attribute: result
    """

    def __init__(
        self,
        type: MessageType,
        content: Union[str, None],
        raw: Union[FeishuEventMessage, DingtalkEventMessage, WeworkEventMessage],
        result: Union[FeishuBaseMessage] = None,
    ):
        super().__init__(type=type, content=content, raw=raw, result=result)

    @property
    def type(self):
        return self["type"]

    @property
    def content(self):
        return self["content"]

    @property
    def raw(self):
        return self["raw"]

    @property
    def result(self):
        return self["result"]
