import logging
import json
from typing import Dict


class Message(Dict):

    def __getattr__(self, name):
        result = self[name]
        if 'message' == name and 'content' in result and isinstance(result['content'], str):
            try:
                result['content'] = json.loads(result['content'])
                # remove @
                for mention in result.get('mentions', []):
                    result['content']['text'] = result['content']['text'].replace(mention['key'] + ' ', '    ')
                # 移除@_all
                result['content']['text'] = result['content']['text'].replace('@_all ', '')
            except Exception as e:
                logging.debug(e)

        return Message(**result) if isinstance(result, dict) else result

