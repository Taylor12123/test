import os
import random

from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    StickerMessage,
    LocationMessage,
    ConfirmTemplate,
    MessageAction,
    TemplateMessage,
    PushMessageRequest
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    StickerMessageContent,
    LocationMessageContent,
    UserSource
)
# 載入資料庫相關函式庫
import pymysql
from sqlalchemy import create_engine

line_access_token = os.environ.get('HtT6YrK6biOfLWO7Osq1/2WWW2BO6Lp4bTWmO5j4ULwmZQT+UQ0QbGbMqSVGt6aYTkQALDRypYWjdJO5SkGE9eIAmTizRKWYVqdQZ3tZPxj6WfneRDfyD1+31GG6zT06ZPaCYCEHgJvGClOjT3l3GQdB04t89/1O/w1cDnyilFU=')
line_secret = os.environ.get('83e4fb858c60d4c83e9919996bea376e')
port_1 = 5000
data_number = 0
category_list = ['王道',' 異世界', '喜劇', '校園', '戀愛', '運動']

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

def Select_data(connection,table_name):
    try:
        # 使用　with...as 可以讓我們程式正確執行接下來自動關閉資料庫連線
        with connection.cursor() as cursor:
            number = 5 * data_number
            sql = f'SELECT * FROM {table_name} LIMIT 5 OFFSET {number}'
            cursor.execute(sql)
            # 取出自訂資料筆數
            result = cursor.fetchall()
            return result
    finally:
        # connection.close()
        pass
def random_Select_data(connection,table_name):
    try:
        # 使用　with...as 可以讓我們程式正確執行接下來自動關閉資料庫連線
        with connection.cursor() as cursor:
            sql = f'SELECT * FROM {table_name}'
            cursor.execute(sql)
            # 取出自訂資料筆數
            result = cursor.fetchall()
            return result
    finally:
        # connection.close()
        pass
'''
若return中有兩個變數 該函數的返回值會以list形式呈現
            
'''

'''使用者狀態管理'''
def Initial_state(connection,user_id):
    try:
        with connection.cursor() as cursor:
            sql = f'''INSERT INTO 使用者狀態(user_id,user_state)
                      VALUES("{user_id}","initial")
                      ON DUPLICATE KEY UPDATE user_state = VALUES(user_state)'''
            cursor.execute(sql)
            connection.commit()
            return user_id
    except Exception as e:
        print(e)
    finally:
        # connection.close()
        pass

def Change_state(connection,user_id,state):
    try:
        with connection.cursor() as cursor:
            sql = f'''UPDATE 使用者狀態
                      SET user_state = "{state}"
                      WHERE user_id = "{user_id}"'''
            cursor.execute(sql)
            connection.commit()
            return state
    except Exception as e:
        print(e)
    finally:
        # connection.close()
        pass

def Select_state(connection,user_id):
    try:
        with connection.cursor() as cursor:
            sql = f'''SELECT user_state
                      FROM  使用者狀態
                      WHERE user_id = "{user_id}"'''
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
    except Exception as e:
        print(e)
    finally:
        # connection.close()
        pass

def clean_state(connection,user_id):
    try:
        with connection.cursor() as cursor:
            sql = f'''UPDATE 使用者狀態
                      SET user_state = "unstarted"
                      WHERE user_id = "{user_id}"'''
            cursor.execute(sql)
            connection.commit()
            return 'unstarted'
    except Exception as e:
        print(e)
    finally:
        connection.close()
        pass


'''linebot'''
def Category(result,msg):
    reply_1 = f'這裡依照近期人氣為您推薦5部｢{msg}｣類別動漫：\n\n'
    for index,value in enumerate(result):
        reply = (f'{index + 1}.『{value["name"]}』\n'
                f'人氣：{value["popularity"]}\n'
                f'上架時間：{value["date"]}\n'
                f'以下是觀看連結：\n'
                f'{value["url"]}\n')
        reply_1 = reply_1 + reply
    return reply_1

def Category_2(result,category):
    reply_1 = f'這裡依照近期人氣為您推薦第{data_number * 5 + 1}~{data_number * 5 + 5}部｢{category}｣類別動漫：\n\n'
    for index,value in enumerate(result):
        reply = (f'{index + (data_number * 5) + 1}.『{value["name"]}』\n'
                f'人氣：{value["popularity"]}\n'
                f'上架時間：{value["date"]}\n'
                f'以接下來是觀看連結：\n'
                f'{value["url"]}\n')
        reply_1 = reply_1 + reply
    return reply_1

def Random(result,user_name):
    reply_1 = f'@{user_name} 您好，想消磨時間卻不知道要看哪一部動漫嗎？\n'\
                      '這裡隨機為您推薦一部人氣動漫\n'\
                      '-------------------------\n'
    value = random.choice(result)
    reply = (f'『{value["name"]}』\n'
            f'人氣：{value["popularity"]}\n'
            f'上架時間：{value["date"]}\n'
            f'以接下來是觀看連結：\n'
            f'{value["url"]}\n')
    reply_1 = reply_1 + reply
    return reply_1

app = Flask(__name__)

configuration = Configuration(access_token='u3o3HIkvtPkLefPE2nPH9CsgzuXVrTTBs23gYGU0AZIrgHrb93zFJ45eQXASyDTNiP7q32LYScKAsq97+8BZ/tj0rHZ+Vg6lSoZJ69RY7bn/d0zJPy+LFnM2W/NzkSWY2vhmqFBF4+q3zEBtirf4pQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler(channel_secret='7ca7268cb8fa26d118120a99a375142b')


@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    print("BODY: ", body)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)

def handle_message(event):
    global data_number
    connect = Connect_Database(host,user,password,database,port)
    # data_number += 1
    user_id = event.source.user_id
    # user_id = '123'
    # print(user_id)
    text = event.message.text
    # Initial_state(connect,user_id)
    # selected_state = Select_state(connect,user_id)[0]['user_state']
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        if text == '愛看啥類別':
            Initial_state(connect,user_id)
            data_number = 0
            latelystate = Change_state(connect,user_id,text)
            # print(user_id)
            print(f'目前狀態:{latelystate}')
            # print(text)
            # print(selected_state)
            # print(selected_state_1)
            if isinstance(event.source, UserSource):
                profile = line_bot_api.get_profile(user_id)
            reply = f'@{profile.display_name} 您好，\n'\
                    '想觀看甚麼類型的動漫呢？\n'\
                    '請選擇想觀看的類型吧!\n'\
                    '(王道、校園、異世界、運動、喜劇、戀愛)'
            line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text = reply)]
                    )
                )
        elif text == '王道':
            selected_state = Select_state(connect,user_id)[0]['user_state']
            if selected_state == '愛看啥類別':
                latelystate = Change_state(connect,user_id,'愛看啥類別-' + text)
                print(f'目前狀態:{latelystate}')
            confirm_template = ConfirmTemplate(
                text='是否加載接下來五部動漫?',
                actions=[
                    MessageAction(label='是', text='是'),
                    MessageAction(label='結束', text='結束')
                ]
            )
            template_message = TemplateMessage(
                alt_text='Confirm alt text',
                template=confirm_template
            )
            data = Select_data(connect,text + '番資料表')
            reply_2 = Category(data,text)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text = reply_2),template_message]
                )
            )

        elif text == '異世界':
            selected_state = Select_state(connect,user_id)[0]['user_state']
            if selected_state == '愛看啥類別':
                latelystate = Change_state(connect,user_id,'愛看啥類別-' + text)
                print(f'目前狀態:{latelystate}')
            confirm_template = ConfirmTemplate(
                text='是否加載接下來五部動漫?',
                actions=[
                    MessageAction(label='是', text='是'),
                    MessageAction(label='結束', text='結束')
                ]
            )
            template_message = TemplateMessage(
                alt_text='Confirm alt text',
                template=confirm_template
            )
            data = Select_data(connect,text + '番資料表')
            reply_2 = Category(data,text)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text = reply_2),template_message]
                )
            )

        elif text == '戀愛':
            selected_state = Select_state(connect,user_id)[0]['user_state']
            if selected_state == '愛看啥類別':
                latelystate = Change_state(connect,user_id,'愛看啥類別-' + text)
                print(f'目前狀態:{latelystate}')
            confirm_template = ConfirmTemplate(
                text='是否加載接下來五部動漫?', 
                actions=[
                    MessageAction(label='是', text='是'),
                    MessageAction(label='結束', text='結束')
                ]
            )
            template_message = TemplateMessage(
                alt_text='Confirm alt text',
                template=confirm_template
            )
            data = Select_data(connect,text + '番資料表')
            reply_2 = Category(data,text)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text = reply_2),template_message]
                )
            )

        elif text == '校園':
            selected_state = Select_state(connect,user_id)[0]['user_state']
            if selected_state == '愛看啥類別':
                latelystate = Change_state(connect,user_id,'愛看啥類別-' + text)
                print(f'目前狀態:{latelystate}')
            confirm_template = ConfirmTemplate(
                text='是否加載接下來五部動漫?',
                actions=[
                    MessageAction(label='是', text='是'),
                    MessageAction(label='結束', text='結束')
                ]
            )
            template_message = TemplateMessage(
                alt_text='Confirm alt text',
                template=confirm_template
            )
            data = Select_data(connect,text + '番資料表')
            reply_2 = Category(data,text)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text = reply_2),template_message]
                )
            )
            
        elif text == '喜劇':
            selected_state = Select_state(connect,user_id)[0]['user_state']
            if selected_state == '愛看啥類別':
                latelystate = Change_state(connect,user_id,'愛看啥類別-' + text)
                print(f'目前狀態:{latelystate}')
            confirm_template = ConfirmTemplate(
                text='是否加載接下來五部動漫?',
                actions=[
                    MessageAction(label='是', text='是'),
                    MessageAction(label='結束', text='結束')
                ]
            )
            template_message = TemplateMessage(
                alt_text='Confirm alt text',
                template=confirm_template
            )
            data = Select_data(connect,text + '番資料表')
            reply_2 = Category(data,text)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text = reply_2),template_message]
                )
            )
        elif text == '運動':
            selected_state = Select_state(connect,user_id)[0]['user_state']
            if selected_state == '愛看啥類別':
                latelystate = Change_state(connect,user_id,'愛看啥類別-' + text)
                print(f'目前狀態:{latelystate}')
            confirm_template = ConfirmTemplate(
                text='是否加載接下來五部動漫?',
                actions=[
                    MessageAction(label='是', text='是'),
                    MessageAction(label='結束', text='結束')
                ]
            )
            template_message = TemplateMessage(
                alt_text='Confirm alt text',
                template=confirm_template
            )
            data = Select_data(connect,text + '番資料表')
            reply_2 = Category(data,text)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text = reply_2),template_message]
                )
            )
        elif text == '今天來看啥':
            state = Change_state(connect,user_id,text)
            print(f'目前狀態:{state}')
            if isinstance(event.source, UserSource):
                profile = line_bot_api.get_profile(user_id)
            confirm_template = ConfirmTemplate(
                text='是否再推薦一部動漫?',
                actions=[
                    MessageAction(label='是', text='是'),
                    MessageAction(label='結束', text='結束')
                ]
            )
            template_message = TemplateMessage(
                alt_text='Confirm alt text',
                template=confirm_template
            )
            random_category = random.choice(category_list) + '番資料表'
            result = random_Select_data(connect,random_category)
            reply = Random(result,profile.display_name)
            line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text = reply),template_message]
                    )
            )
        if text == '是':
            selected_state = Select_state(connect,user_id)[0]['user_state']
            if  selected_state == '愛看啥類別-王道':
                data_number += 1
                confirm_template = ConfirmTemplate(
                    text='是否加載接下來五部動漫?',
                    actions=[
                        MessageAction(label='是', text='是'),
                        MessageAction(label='結束', text='結束')
                    ]
                )
                template_message = TemplateMessage(
                    alt_text='Confirm alt text',
                    template=confirm_template
                )
                data = Select_data(connect,'王道番資料表')
                reply_2 = Category_2(data,'王道')
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text = reply_2),template_message]
                    )
                )
        # elif text == '是':
        #     selected_state = Select_state(connect,user_id)[0]['user_state']
            elif selected_state == '愛看啥類別-異世界':
                data_number += 1
                confirm_template = ConfirmTemplate(
                    text='是否加載接下來五部動漫?',
                    actions=[
                        MessageAction(label='是', text='是'),
                        MessageAction(label='結束', text='結束')
                    ]
                )
                template_message = TemplateMessage(
                    alt_text='Confirm alt text',
                    template=confirm_template
                )
                data = Select_data(connect,'異世界番資料表')
                reply_2 = Category_2(data,'異世界')
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text = reply_2),template_message]
                    )
                )
        # elif text == '是':
        #     selected_state = Select_state(connect,user_id)[0]['user_state']
            elif selected_state == '愛看啥類別-喜劇':
                data_number += 1
                confirm_template = ConfirmTemplate(
                    text='是否加載接下來五部動漫?',
                    actions=[
                        MessageAction(label='是', text='是'),
                        MessageAction(label='結束', text='結束')
                    ]
                )
                template_message = TemplateMessage(
                    alt_text='Confirm alt text',
                    template=confirm_template
                )
                data = Select_data(connect,'喜劇番資料表')
                reply_2 = Category_2(data,'喜劇')
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text = reply_2),template_message]
                    )
                )
        # elif text == '是':
        #     selected_state = Select_state(connect,user_id)[0]['user_state']
            elif selected_state == '愛看啥類別-校園':
                data_number += 1
                confirm_template = ConfirmTemplate(
                    text='是否加載接下來五部動漫?',
                    actions=[
                        MessageAction(label='是', text='是'),
                        MessageAction(label='結束', text='結束')
                    ]
                )
                template_message = TemplateMessage(
                    alt_text='Confirm alt text',
                    template=confirm_template
                )
                data = Select_data(connect,'校園番資料表')
                reply_2 = Category_2(data,'校園')
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text = reply_2),template_message]
                    )
                )
        # elif text == '是':
        #     selected_state = Select_state(connect,user_id)[0]['user_state']
            elif selected_state == '愛看啥類別-戀愛':
                data_number += 1
                confirm_template = ConfirmTemplate(
                    text='是否加載接下來五部動漫?',
                    actions=[
                        MessageAction(label='是', text='是'),
                        MessageAction(label='結束', text='結束')
                    ]
                )
                template_message = TemplateMessage(
                    alt_text='Confirm alt text',
                    template=confirm_template
                )
                data = Select_data(connect,'戀愛番資料表')
                reply_2 = Category_2(data,'戀愛')
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text = reply_2),template_message]
                    )
                )
        # elif text == '是':
        #     selected_state = Select_state(connect,user_id)[0]['user_state']
            elif selected_state == '愛看啥類別-運動':
                data_number += 1
                confirm_template = ConfirmTemplate(
                    text='是否加載接下來五部動漫?',
                    actions=[
                        MessageAction(label='是', text='是'),
                        MessageAction(label='結束', text='結束')
                    ]
                )
                template_message = TemplateMessage(
                    alt_text='Confirm alt text',
                    template=confirm_template
                )
                data = Select_data(connect,'運動番資料表')
                reply_2 = Category_2(data,'運動')
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text = reply_2),template_message]
                    )
                )
            # if text == '是':
            #     selected_state = Select_state(connect,user_id)[0]['user_state']
            elif selected_state == '今天來看啥':
                if isinstance(event.source, UserSource):
                    profile = line_bot_api.get_profile(user_id)
                confirm_template = ConfirmTemplate(
                    text='是否再推薦一部動漫?',
                    actions=[
                        MessageAction(label='是', text='是'),
                        MessageAction(label='結束', text='結束')
                    ]
                )
                template_message = TemplateMessage(
                    alt_text='Confirm alt text',
                    template=confirm_template
                )
                random_category = random.choice(category_list) + '番資料表'
                result = random_Select_data(connect,random_category)
                reply = Random(result,profile.display_name)
                line_bot_api.reply_message_with_http_info(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text = reply),template_message]
                        )
                )
        if text == '結束':
            latelystate = clean_state(connect,user_id)
            print(f'目前狀態:{latelystate}')
            msg = '感謝您的使用~~~'
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text = msg)]
                )
            )
        

@handler.add(MessageEvent, message=StickerMessageContent)
def handle_sticker_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[StickerMessage(
                    package_id=event.message.package_id,
                    sticker_id=event.message.sticker_id)
                ]
            )
        )

if __name__ == "__main__":
    app.run(port=port_1)
    # x = Connect_Database(host,user,password,database,port)
    # x.close()
    