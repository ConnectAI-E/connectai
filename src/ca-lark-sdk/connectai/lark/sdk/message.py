import json
from typing import Dict, List


# 以下为飞书消息
class FeishuBaseMessage(Dict):
    msg_type = "unkown"


class FeishuTextMessage(FeishuBaseMessage):
    msg_type = "text"

    def __init__(self, text=""):
        super().__init__(text=text)


class FeishuImageMessage(FeishuBaseMessage):
    msg_type = "image"

    def __init__(self, image_key=""):
        super().__init__(image_key=image_key)


class FeishuPostMessage(FeishuBaseMessage):
    msg_type = "post"

    def __init__(self, *content, title="", lang="zh_cn"):
        super().__init__(**{lang: dict(title=title, content=list(content))})


class FeishuPostMessageTag(Dict):
    def __init__(self, tag="text", style=None, **kwargs):
        if style:
            super().__init__(tag=tag, style=style, **kwargs)
        else:
            super().__init__(tag=tag, **kwargs)


class FeishuPostMessageText(FeishuPostMessageTag):
    def __init__(self, text="", un_escape=False, style=None):
        super().__init__(tag="text", text=text, un_escape=un_escape, style=style)


class FeishuPostMessageA(FeishuPostMessageTag):
    def __init__(self, text="", href="", style=None):
        super().__init__(tag="a", text=text, href=href, style=style)


class FeishuPostMessageAt(FeishuPostMessageTag):
    def __init__(self, user_id="", style=None):
        super().__init__(tag="at", user_id=user_id, style=style)


class FeishuPostMessageImage(Dict):
    def __init__(self, image_key=""):
        super().__init__(tag="img", image_key=image_key)


class FeishuPostMessageMedia(Dict):
    def __init__(self, file_key="", image_key=""):
        super().__init__(tag="media", file_key=file_key, image_key=image_key)


class FeishuPostMessageEmotion(Dict):
    def __init__(self, emoji_type=""):
        super().__init__(tag="emotion", emoji_type=emoji_type)


class FeishuShareChatMessage(FeishuBaseMessage):
    msg_type = "share_chat"

    def __init__(self, chat_id=""):
        super().__init__(chat_id=chat_id)


class FeishuShareUserMessage(FeishuBaseMessage):
    msg_type = "share_user"

    def __init__(self, user_id=""):
        super().__init__(user_id=user_id)


class FeishuFileMessage(FeishuBaseMessage):
    msg_type = "file"

    def __init__(self, file_key=""):
        super().__init__(file_key=file_key)


class FeishuAudioMessage(FeishuFileMessage):
    msg_type = "audio"


class FeishuStickerMessage(FeishuFileMessage):
    msg_type = "sticker"


class FeishuMediaMessage(FeishuBaseMessage):
    msg_type = "media"

    def __init__(self, file_key="", image_key=""):
        super().__init__(file_key=file_key, image_key=image_key)


class FeishuMessageCardConfig(Dict):
    def __init__(self, update_multi=True, enable_forward=True):
        super().__init__(update_multi=update_multi, enable_forward=enable_forward)


class FeishuMessageCardHeader(Dict):
    def __init__(self, content="", tag="plain_text", template="default"):
        super().__init__(title=dict(tag=tag, content=content), template=template)


class FeishuMessageCard(FeishuBaseMessage):
    msg_type = "interactive"

    def __init__(self, *elements, header=None, config=None):
        if isinstance(header, str):
            header = FeishuMessageCardHeader(header)
        elif not header:
            header = FeishuMessageCardHeader()

        if not config:
            config = FeishuMessageCardConfig()

        super().__init__(header=header, elements=elements, config=config)


class FeishuMessageHr(Dict):
    def __init__(self):
        super().__init__(tag="hr")


class FeishuMessageDiv(Dict):
    def __init__(self, content="", tag="plain_text", **kwargs):
        super().__init__(
            tag="div",
            text=dict(
                tag=tag,
                content=content,
            ),
            **kwargs,
        )


# https://open.feishu.cn/document/common-capabilities/message-card/add-card-interaction/interactive-components/button
class FeishuMessageButton(Dict):
    def __init__(
        self, content="", tag="plain_text", value=None, type="default", **kwargs
    ):
        super().__init__(
            tag="button",
            text=dict(tag=tag, content=content),
            value=value or dict(),
            type=type,
            **kwargs,
        )


class FeishuMessageAction(Dict):
    def __init__(self, *actions, layout="flow"):
        super().__init__(tag="action", layout=layout, actions=actions)


class FeishuMessageOption(Dict):
    def __init__(self, value="", content="", tag="plain_text"):
        super().__init__(value=value, text=dict(tag=tag, content=content or value))


class FeishuMessageSelect(Dict):
    def __init__(self, *options, placeholder="", tag="plain_text", **kwargs):
        super().__init__(
            tag="select_static",
            placeholder=dict(tag=tag, content=placeholder),
            options=options,
            **kwargs,
        )


class FeishuMessageOverflow(Dict):
    def __init__(self, *options, placeholder="", tag="plain_text", **kwargs):
        super().__init__(
            tag="overflow",
            placeholder=dict(tag=tag, content=placeholder),
            options=options,
            **kwargs,
        )


class FeishuMessageSelectPerson(Dict):
    def __init__(self, *persons, placeholder="", tag="plain_text", **kwargs):
        super().__init__(
            tag="select_person",
            placeholder=dict(tag=tag, content=placeholder),
            options=[{"value": v} if isinstance(v, str) else v for v in persons],
            **kwargs,
        )


class FeishuMessageDatePicker(Dict):
    def __init__(self, content="Please select date", tag="plain_text"):
        super().__init__(tag="date_picker", placeholder=dict(tag=tag, content=content))


class FeishuMessagePlainText(Dict):
    def __init__(self, content=""):
        super().__init__(tag="plain_text", content=content)


class FeishuMessageMDText(Dict):
    def __init__(self, content=""):
        super().__init__(tag="lark_md", content=content)


class FeishuMessageLarkMD(Dict):
    def __init__(self, content="", is_short=False):
        super().__init__(
            is_short=is_short,
            text=dict(
                tag="lark_md",
                content=content,
            ),
        )


class FeishuMessageImage(Dict):
    def __init__(self, img_key="", alt="", tag="", mode="fit_horizontal", preview=True):
        super().__init__(
            tag="img",
            img_key=img_key,
            alt=dict(tag=tag, content=alt),
            mode=mode,
            preview=preview,
        )


class FeishuMessageMarkdown(Dict):
    def __init__(self, content="", **kwargs):
        super().__init__(tag="markdown", content=content, **kwargs)


class FeishuMessageNote(Dict):
    def __init__(self, *elements):
        super().__init__(tag="note", elements=elements)


class FeishuMessageConfirm(Dict):
    def __init__(self, title="", text=""):
        super().__init__(
            title=dict(tag="plain_text", content=title),
            text=dict(tag="plain_text", content=text),
        )


class FeishuMessageColumnSet(Dict):
    def __init__(self, *columns, flex_mode="none", background_style="grey"):
        super().__init__(
            tag="column_set",
            flex_mode=flex_mode,
            background_style=background_style,
            columns=columns,
        )


class FeishuMessageColumn(Dict):
    def __init__(self, *elements, width="weighted", weight=1, vertical_align="top"):
        super().__init__(
            tag="column",
            width=width,
            weight=weight,
            vertical_align=vertical_align,
            elements=elements,
        )
