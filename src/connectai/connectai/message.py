import json
import logging
from typing import Dict


class Message(Dict):
    def __getattribute__(self, name):
        if name in self:
            result = self[name]
            if name == "result":
                return result

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
