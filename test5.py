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
    ConfirmTemplate,
    MessageAction,
    TemplateMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    UserSource
)

app = Flask(__name__)

configuration = Configuration(access_token='HtT6YrK6biOfLWO7Osq1/2WWW2BO6Lp4bTWmO5j4ULwmZQT+UQ0QbGbMqSVGt6aYTkQALDRypYWjdJO5SkGE9eIAmTizRKWYVqdQZ3tZPxj6WfneRDfyD1+31GG6zT06ZPaCYCEHgJvGClOjT3l3GQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler(channel_secret='83e4fb858c60d4c83e9919996bea376e')


@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
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
    text = event.message.text
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        if text == 'confirm':
            confirm_template = ConfirmTemplate(
                text='Do it?',
                actions=[
                    MessageAction(label='Yes', text='Yes!'),
                    MessageAction(label='No', text='No!')
                ]
            )
            template_message = TemplateMessage(
                alt_text='Confirm alt text',
                template=confirm_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[template_message]
                )
            )
        if text == 'profile':
            if isinstance(event.source, UserSource):
                profile = line_bot_api.get_profile(user_id=event.source.user_id)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[
                            TextMessage(text='Display name: ' + profile.display_name),
                            TextMessage(text='Status message: ' + str(profile.status_message))
                        ]
                    )
                )

if __name__ == "__main__":
    app.run()