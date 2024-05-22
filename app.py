import os
import random
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    StickerMessage,
    ConfirmTemplate,
    MessageAction,
    TemplateMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent, StickerMessageContent, UserSource
import pymysql

# Configurations and credentials
line_access_token = os.environ.get('HtT6YrK6biOfLWO7Osq1/2WWW2BO6Lp4bTWmO5j4ULwmZQT+UQ0QbGbMqSVGt6aYTkQALDRypYWjdJO5SkGE9eIAmTizRKWYVqdQZ3tZPxj6WfneRDfyD1+31GG6zT06ZPaCYCEHgJvGClOjT3l3GQdB04t89/1O/w1cDnyilFU=')
line_secret = os.environ.get('83e4fb858c60d4c83e9919996bea376e')
port_1 = 5000
data_number = 0
category_list = ['王道', '異世界', '喜劇', '校園', '戀愛', '運動']

# Database configurations
host = '0.0.0.0'
user = 'root'
password = ''
database = 'acg資料庫'
port = 3306

# Database connection
def connect_database():
    connection = pymysql.connect(host=host,
                                 user=user,
                                 password=password,
                                 port=port,
                                 db=database,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

def select_data(connection, table_name, offset):
    with connection.cursor() as cursor:
        sql = f'SELECT * FROM {table_name} LIMIT 5 OFFSET {offset}'
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

def random_select_data(connection, table_name):
    with connection.cursor() as cursor:
        sql = f'SELECT * FROM {table_name}'
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

# User state management
def initial_state(connection, user_id):
    with connection.cursor() as cursor:
        sql = f'''INSERT INTO 使用者狀態(user_id, user_state)
                  VALUES("{user_id}", "initial")
                  ON DUPLICATE KEY UPDATE user_state = VALUES(user_state)'''
        cursor.execute(sql)
        connection.commit()

def change_state(connection, user_id, state):
    with connection.cursor() as cursor:
        sql = f'''UPDATE 使用者狀態
                  SET user_state = "{state}"
                  WHERE user_id = "{user_id}"'''
        cursor.execute(sql)
        connection.commit()

def select_state(connection, user_id):
    with connection.cursor() as cursor:
        sql = f'''SELECT user_state
                  FROM 使用者狀態
                  WHERE user_id = "{user_id}"'''
        cursor.execute(sql)
        result = cursor.fetchone()
        return result['user_state']

def clean_state(connection, user_id):
    with connection.cursor() as cursor:
        sql = f'''UPDATE 使用者狀態
                  SET user_state = "unstarted"
                  WHERE user_id = "{user_id}"'''
        cursor.execute(sql)
        connection.commit()

# Linebot reply functions
def format_category(result, category):
    reply = f'這裡依照近期人氣為您推薦5部「{category}」類別動漫：\n\n'
    for index, value in enumerate(result):
        reply += (f'{index + 1}.『{value["name"]}』\n'
                  f'人氣：{value["popularity"]}\n'
                  f'上架時間：{value["date"]}\n'
                  f'以下是觀看連結：\n'
                  f'{value["url"]}\n\n')
    return reply

def format_category_pagination(result, category, offset):
    start_num = offset * 5 + 1
    end_num = start_num + len(result) - 1
    reply = f'這裡依照近期人氣為您推薦第{start_num}~{end_num}部「{category}」類別動漫：\n\n'
    for index, value in enumerate(result, start=start_num):
        reply += (f'{index}.『{value["name"]}』\n'
                  f'人氣：{value["popularity"]}\n'
                  f'上架時間：{value["date"]}\n'
                  f'以下是觀看連結：\n'
                  f'{value["url"]}\n\n')
    return reply

def format_random(result, user_name):
    value = random.choice(result)
    reply = (f'@{user_name} 您好，想消磨時間卻不知道要看哪一部動漫嗎？\n'
             '這裡隨機為您推薦一部人氣動漫：\n'
             '-------------------------\n'
             f'『{value["name"]}』\n'
             f'人氣：{value["popularity"]}\n'
             f'上架時間：{value["date"]}\n'
             f'以下是觀看連結：\n'
             f'{value["url"]}\n')
    return reply

app = Flask(__name__)

configuration = Configuration(access_token='HtT6YrK6biOfLWO7Osq1/2WWW2BO6Lp4bTWmO5j4ULwmZQT+UQ0QbGbMqSVGt6aYTkQALDRypYWjdJO5SkGE9eIAmTizRKWYVqdQZ3tZPxj6WfneRDfyD1+31GG6zT06ZPaCYCEHgJvGClOjT3l3GQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler(channel_secret='83e4fb858c60d4c83e9919996bea376e')

@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    global data_number
    text = event.message.text
    user_id = event.source.user_id

    connect = connect_database()
    user_state = select_state(connect, user_id)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        if text == '愛看啥類別':
            initial_state(connect, user_id)
            data_number = 0
            change_state(connect, user_id, text)
            profile = line_bot_api.get_profile(user_id) if isinstance(event.source, UserSource) else None
            reply = (f'@{profile.display_name} 您好，\n'
                     '想觀看甚麼類型的動漫呢？\n'
                     '請選擇想觀看的類型吧!\n'
                     '(王道、校園、異世界、運動、喜劇、戀愛)')
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply)]
                )
            )
        elif text in category_list:
            if user_state == '愛看啥類別':
                change_state(connect, user_id, f'愛看啥類別-{text}')
            data = select_data(connect, f'{text}番資料表', data_number * 5)
            reply_2 = format_category(data, text)
            confirm_template = ConfirmTemplate(
                text='是否加載接下來五部動漫?',
                actions=[MessageAction(label='是', text='是'), MessageAction(label='結束', text='結束')]
            )
            template_message = TemplateMessage(alt_text='Confirm alt text', template=confirm_template)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_2), template_message]
                )
            )
        elif text == '今天來看啥':
            change_state(connect, user_id, text)
            profile = line_bot_api.get_profile(user_id) if isinstance(event.source, UserSource) else None
            random_category = random.choice(category_list) + '番資料表'
            result = random_select_data(connect, random_category)
            reply = format_random(result, profile.display_name)
            confirm_template = ConfirmTemplate(
                text='是否再推薦一部動漫?',
                actions=[MessageAction(label='是', text='是'), MessageAction(label='結束', text='結束')]
            )
            template_message = TemplateMessage(alt_text='Confirm alt text', template=confirm_template)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply), template_message]
                )
            )
        elif text == '是':
            user_state = select_state(connect, user_id)
            category = user_state.split('-')[-1]
            data_number += 1
            data = select_data(connect, f'{category}番資料表', data_number * 5)
            reply_2 = format_category_pagination(data, category, data_number)
            confirm_template = ConfirmTemplate(
                text='是否加載接下來五部動漫?',
                actions=[MessageAction(label='是', text='是'), MessageAction(label='結束', text='結束')]
            )
            template_message = TemplateMessage(alt_text='Confirm alt text', template=confirm_template)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_2), template_message]
                )
            )
        elif text == '結束':
            clean_state(connect, user_id)
            msg = '感謝您的使用~~~'
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=msg)]
                )
            )

@handler.add(MessageEvent, message=StickerMessageContent)
def handle_sticker(event):
    package_id = event.message.package_id
    sticker_id = event.message.sticker_id
    sticker_message = StickerMessage(package_id=package_id, sticker_id=sticker_id)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[sticker_message]
            )
        )

if __name__ == "__main__":
    app.run(port=port_1)
