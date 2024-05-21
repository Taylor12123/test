from flask import Flask, request

# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, StickerSendMessage, ImageSendMessage, LocationSendMessage
# 注意，有載入 StickerSendMessage 模組

import json

app = Flask(__name__)


@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)                # 取得收到的訊息內容
    # try:
    json_data = json.loads(body)                         # json 格式化訊息內容
    access_token = 'HtT6YrK6biOfLWO7Osq1/2WWW2BO6Lp4bTWmO5j4ULwmZQT+UQ0QbGbMqSVGt6aYTkQALDRypYWjdJO5SkGE9eIAmTizRKWYVqdQZ3tZPxj6WfneRDfyD1+31GG6zT06ZPaCYCEHgJvGClOjT3l3GQdB04t89/1O/w1cDnyilFU='
    secret = '83e4fb858c60d4c83e9919996bea376e'
    line_bot_api = LineBotApi(access_token)              # 確認 token 是否正確
    handler = WebhookHandler(secret)                     # 確認 secret 是否正確
    signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
    handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
    tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
    try :
        stickerId = json_data['events'][0]['message']['stickerId'] # 取得 stickerId
        packageId = json_data['events'][0]['message']['packageId'] # 取得 packageId
        sticker_message = StickerSendMessage(sticker_id=stickerId, package_id=packageId) # 設定要回傳的表情貼圖
        line_bot_api.reply_message(tk, sticker_message)  # 回傳訊息
    except:
        msg = json_data['events'][0]['message']['text']
        if msg == '皮卡丘':
            # 如果有圖片網址，回傳圖片
            img_url = 'https://upload.wikimedia.org/wikipedia/en/a/a6/Pok%C3%A9mon_Pikachu_art.png'
            img_message = ImageSendMessage(original_content_url=img_url, preview_image_url=img_url)
            line_bot_api.reply_message(tk,img_message)
        elif msg == '101':
            # 如果有地點資訊，回傳地點
            location_message = LocationSendMessage(title='台北 101',
                                                    address='110台北市信義區信義路五段7號',
                                                    latitude='25.034095712145003',
                                                    longitude='121.56489941996108')
            line_bot_api.reply_message(tk,location_message)
        else:
            line_bot_api.reply_message(tk,TextSendMessage(msg))
    return 'OK'                 # 驗證 Webhook 使用，不能省略
if __name__ == "__main__":
    app.run()