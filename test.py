# from connectai import *
import connectai as ca



with ca.MessageBroker() as broker:
    ca.NoopEventHandler(1)
    with ca.FeishuChatBot(app_id=1) as bot:
        pass
    with ca.FeishuChatBot(app_id=2) as bot:
        pass


if __name__ == "__main__":
    import asyncio
    asyncio.run(broker.launch())

