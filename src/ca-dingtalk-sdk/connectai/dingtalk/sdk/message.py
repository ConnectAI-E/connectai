from typing import Dict


# 以下为钉钉消息
# https://open.dingtalk.com/document/isvapp/message-types-supported-by-enterprise-internal-robots-1
class DingtalkBaseMessage(Dict):
    msgtype = "unkown"

    def __init__(
        self, atMobiles=list(), atUserIds=list(), isAtAll=False, at=True, **kwargs
    ):
        # actionCard/feedCard no need at.
        if at:
            kwargs["at"] = dict(
                atMobiles=atMobiles,
                atUserIds=atUserIds,
                isAtAll=isAtAll,
            )
        super().__init__(msgtype=self.msgtype, **kwargs)


class DingtalkTextMessage(DingtalkBaseMessage):
    msgtype = "text"

    def __init__(self, content="", **kwargs):
        super().__init__(text=dict(content=content), **kwargs)


class DingtalkLinkMessage(DingtalkBaseMessage):
    msgtype = "link"

    def __init__(self, text="", title="", messageUrl="", picUrl="", **kwargs):
        super().__init__(
            link=dict(
                text=text,
                title=title,
                picUrl=picUrl,
                messageUrl=messageUrl,
            ),
            **kwargs
        )


class DingtalkMarkdownMessage(DingtalkBaseMessage):
    msgtype = "markdown"

    def __init__(self, title="", text="", **kwargs):
        super().__init__(markdown=dict(title=title, text=text), **kwargs)


class DingtalkActionCardButton(Dict):
    def __init__(self, actionURL="", title=""):
        super().__init__(actionURL=actionURL, title=title)


class DingDingActionCardMessage(DingtalkBaseMessage):
    msgtype = "actionCard"

    def __init__(
        self, *btn, btns=list(), title="", text="", btnOrientation="0", **kwargs
    ):
        super().__init__(
            actionCard=dict(
                title=title,
                text=text,
                btnOrientation=str(btnOrientation),
                btns=btns + list(btn),
            ),
            at=False,
        )


class DingtalkFeedCardLink(Dict):
    def __init__(self, messageURL="", picURL="", title=""):
        super().__init__(messageURL=messageURL, picURL=picURL, title=title)


class DingtalkFeedCardMessage(DingtalkBaseMessage):
    msgtype = "feedCard"

    def __init__(self, *link, links=list(), **kwargs):
        super().__init__(
            feedCard=dict(
                links=links + list(link),
            ),
            at=False,
        )
