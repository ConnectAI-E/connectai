from connectai import *
import connectai as ca

def reply_text2(message):
    print('reply_text', message)
    # 这里可以利用contextvar拿到当前对应的message_ctx里面的数据
    print('reply_text current_bot', current_bot, message_ctx.app_id, message_ctx.message)
    return 'reply2 ' + message['content']

with ca.MessageBroker() as broker:
    ca.NoopEventHandler(1)
    with ca.FeishuChatBot(app_id=1) as bot:
        # 支持一个event多个回调函数
        bot.send_text(reply_text2)
        pass
    with ca.FeishuChatBot(app_id=2) as bot:
        pass


if __name__ == "__main__":
    broker.launch()

