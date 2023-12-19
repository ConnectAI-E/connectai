import json
import logging
from typing import Dict


class Message(Dict):
    def __getattribute__(self, name):
        if name in self:
            result = self[name]
            if name == "result":
                return result
            if (
                "message" == name
                and "content" in result
                and isinstance(result["content"], str)
            ):
                try:
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

            return Message(**result) if isinstance(result, dict) else result
        return super().__getattribute__(name)
