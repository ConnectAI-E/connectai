import json
from typing import Dict


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
        self, content="", tag="plain_text", value=dict(), type="default", **kwargs
    ):
        super().__init__(
            tag="button",
            text=dict(tag=tag, content=content),
            value=value,
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
