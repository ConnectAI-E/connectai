# 企联AI Dev

ConnectAI定位为一个帮助公司更快地建立AI内部工具的平台


## 产品背景

1. 由于各个公司的内部管理流程不同，会有很多无法标准化的长尾AI需求
2. 企业内部技术团队需要将1/3的时间用来开发维护这些内部AI工具
3. 如果能将低代码用于AI内部工具的开发，无疑将极大地提升企业技术团队的效率
4. 既然AI需求是无法标准化的，那么就标准化这些长尾AI需求的开发工具
5. 以低代码的方式提高内部AI工具开发效率


# ca-lark-webhook

1. 生成飞书(Lark) webhook回调接口
2. 注册处理对应事件的回调方法


## python sdk
```
from connectai.lark.webhook import LarkServer

app = LarkServer()

@app.on_bot_message(app_id='cli_xxx', app_secret='xxx', encrypt_key='xxx', message_type='text')
def on_message_callback1(bot, message_id, content, **kwargs):
    text = content['text']
    bot.reply_text(message_id, 'reply: ' + text)

app.start(host='0.0.0.0', port=8888)
```
