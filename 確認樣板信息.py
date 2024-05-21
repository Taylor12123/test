from flask import Flask, request
import json
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ConfirmTemplate, TemplateSendMessage, MessageAction

app = Flask(__name__)

@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)  # 取得收到的訊息內容
    try:
        json_data = json.loads(body)  # json 格式化訊息內容
        access_token = 'HtT6YrK6biOfLWO7Osq1/2WWW2BO6Lp4bTWmO5j4ULwmZQT+UQ0QbGbMqSVGt6aYTkQALDRypYWjdJO5SkGE9eIAmTizRKWYVqdQZ3tZPxj6WfneRDfyD1+31GG6zT06ZPaCYCEHgJvGClOjT3l3GQdB04t89/1O/w1cDnyilFU='
        secret = '83e4fb858c60d4c83e9919996bea376e'
        line_bot_api = LineBotApi(access_token)  # 確認 token 是否正確
        handler = WebhookHandler(secret)  # 確認 secret 是否正確
        signature = request.headers['X-Line-Signature']  # 加入回傳的 headers
        handler.handle(body, signature)  # 綁定訊息回傳的相關資訊

        # 取得訊息相關資訊
        event = json_data['events'][0]
        reply_token = event['replyToken']
        message_type = event['message']['type']
        message_text = event['message']['text']

        # 根據收到的訊息類型進行處理
        if message_type == 'text':
            if message_text == '確認模板':
                # 建立確認模板
                confirm_template = ConfirmTemplate(
                    text='是否加載下五部動漫',
                    actions=[
                        MessageAction(label='是', text='是'),
                        MessageAction(label='否', text='否')
                    ]
                )
                # 建立 TemplateSendMessage
                template_message = TemplateSendMessage(alt_text='確認模板', template=confirm_template)
                # 回覆確認模板訊息
                line_bot_api.reply_message(reply_token, template_message)
            else:
                # 其他文字訊息的回覆
                line_bot_api.reply_message(
                    reply_token,
                    TextSendMessage(text=message_text)
                )

    except Exception as e:
        print(e)  # 如果發生錯誤，印出錯誤訊息

    return 'OK'  # 驗證 Webhook 使用，不能省略

if __name__ == "__main__":
    app.run()
