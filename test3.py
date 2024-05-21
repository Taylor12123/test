from flask import Flask, request

# 載入 json 標準函式庫，處理回傳的資料格式
import json

# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, MessageAction, TemplateSendMessage, ConfirmTemplate
# 載入資料庫相關函式庫
import pandas as pd
import pymysql
from sqlalchemy import create_engine

'''資料庫連結'''

host = '127.0.0.1'
user = 'root'
password = ''
database = 'acg資料庫'
port = 3306

def Connect_Database(host,user,password,database,port):
    connection = pymysql.connect(host=host,
                                user=user,
                                password=password,
                                port=port,
                                db=database,
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    return connection

def Select_data(connection,table_name,data_mumber):
    try:
        # 使用　with...as 可以讓我們程式正確執行下自動關閉資料庫連線
        with connection.cursor() as cursor:
            sql = f'SELECT * FROM {table_name} LIMIT 5 OFFSET {5 * data_mumber}'
            cursor.execute(sql)
            # 取出自訂資料筆數
            result = cursor.fetchall()
            return result
    finally:
        connection.close()

'''linebot'''
def Category(msg,connect):
    data = Select_data(connect,msg + '番資料庫',1)
    reply_1 = f'這裡依照近期人氣為您推薦五部｢{msg}｣類別動漫：\n\n'
    for index,value in enumerate(data):
        reply = (f'{index + 1}.『{value["name"]}』\n'
                f'人氣：{value["popularity"]}\n'
                f'上架時間：{value["date"]}\n'
                f'以下是觀看連結：\n'
                f'{value["url"]}\n')
        reply_1 = reply_1 + reply
    return reply_1

app = Flask(__name__)
@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)                      # 取得收到的訊息內容
    try:
        json_data = json.loads(body)                           # json 格式化訊息內容
        access_token = 'HtT6YrK6biOfLWO7Osq1/2WWW2BO6Lp4bTWmO5j4ULwmZQT+UQ0QbGbMqSVGt6aYTkQALDRypYWjdJO5SkGE9eIAmTizRKWYVqdQZ3tZPxj6WfneRDfyD1+31GG6zT06ZPaCYCEHgJvGClOjT3l3GQdB04t89/1O/w1cDnyilFU='
        secret = '83e4fb858c60d4c83e9919996bea376e'
        line_bot_api = LineBotApi(access_token)                # 確認 token 是否正確
        handler = WebhookHandler(secret)                       # 確認 secret 是否正確
        signature = request.headers['X-Line-Signature']        # 加入回傳的 headers
        handler.handle(body, signature)                        # 綁定訊息回傳的相關資訊
        tk = json_data['events'][0]['replyToken']              # 取得回傳訊息的 Token
        # type = json_data['events'][0]['message']['type']     # 取得 LINE 收到的訊息類型
        msg = json_data['events'][0]['message']['text']        # 取得 LINE 收到的文字訊息
        connect = Connect_Database(host,user,password,database,port)
        if msg == '運動':
            reply_2 = Category(msg,connect)
            line_bot_api.reply_message(tk,TextSendMessage(reply_2))   # 回傳訊息
        elif msg == '王道':
            Category(msg,connect)
            line_bot_api.reply_message(tk,TextSendMessage(reply_2))   # 回傳訊息
        elif msg == '喜劇':
            Category(msg,connect)
            line_bot_api.reply_message(tk,TextSendMessage(reply_2))   # 回傳訊息
        elif msg == '校園':
            Category(msg,connect)
            line_bot_api.reply_message(tk,TextSendMessage(reply_2))   # 回傳訊息
        elif msg == '戀愛':
            Category(msg,connect)
            line_bot_api.reply_message(tk,TextSendMessage(reply_2))   # 回傳訊息
        elif msg == '異世界':
            Category(msg,connect)
            line_bot_api.reply_message(tk,TextSendMessage(reply_2))   # 回傳訊息
        
    except:
        print(body)                                            # 如果發生錯誤，印出收到的內容
    return 'OK'                                                # 驗證 Webhook 使用，不能省略

if __name__ == "__main__":
    app.run()