import os
import re
import openai
import emoji
from flask import Flask, request, abort
from src.completion_handler import completion_heandler
from src.configs import DEVELOPE_MODE_STRING, SUMMARY_ASSISTANT_STRING
from src.youtube_handler import YT_handler

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (
    ButtonsTemplate, ImageSendMessage,
    MessageEvent, PostbackTemplateAction,
    TemplateSendMessage, TextMessage, URITemplateAction
)

app = Flask(__name__)
user_id = os.getenv("OPENAI_API_KEY")

channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)

print(f"channel_access_token = {channel_access_token}")
print(f"channel_secret = {channel_secret}")
line_bot_api = LineBotApi(
    "qeo54kjTJllTZD/23THmmgBSic/pDlZClfh9w/+Cdq8fqhNUENUEUpWPWacqJyhAyVPNfs5sWYdku0O3jMOF1M2EHghrbbuLvpy/sLBghRf8430tNXnm+cTOotZsW4489RdwLoM/dw4PERM8Jmue8AdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler("bb01007222d61a3b4471c1e2fc604db5")

prompts = completion_heandler(system_message="You are a helpful assistant.",
                              message_count=5)
msg_management = {}


@app.route("/", methods=("GET", "POST"))
def root():
    return "Build web success!"


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
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
        abort(400)
    return 'OK'


BUTTONS_TEMPLATE_MESSAGE = ButtonsTemplate(
    thumbnail_image_url="https://i.imgur.com/i8tEmlY.jpg",
    title='chatgpt相關網頁',
    text='選擇動作',
    ratio="1.51:1",
    image_size="cover",
    actions=[
        # PostbackTemplateAction 點擊選項後，
        # 除了文字會顯示在聊天室中，
        # 還回傳data中的資料，可
        # 此類透過 Postback event 處理。
        URITemplateAction(label='chatGPT指令大全',
                          uri='https://www.explainthis.io/zh-hant/chatgpt'),
        URITemplateAction(label='chatGPT web chat',
                          uri='https://chat.openai.com/chat'),
        URITemplateAction(label='chatGPT API 文件',
                          uri='https://platform.openai.com/docs/api-reference'),
        URITemplateAction(label='chatGPT examples',
                          uri='https://platform.openai.com/examples')
    ])


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id

    print(f"user: {user_id}, message: {event.message.text}")
    if event.message.text == "/選單":
        msg = TemplateSendMessage(alt_text="chatGPT相關網頁",
                                  template=BUTTONS_TEMPLATE_MESSAGE)
    elif event.message.text == "/指令":
        msg = TextMessage(text=emoji.emojize(
            "以下是機器人支援的指令:\n" +
            "/角色 :arrow_right:告訴機器人他是什麼角色，有助於產生更好的結果，例如:/角色 你是一位專業股票分析師\n" +
            "/圖片 :arrow_right:依照條件產出圖片，例如:/圖片 給我一張海邊風景圖\n" +
            "/清除 :arrow_right:讓機器人忘掉之前的對話\n" + "/選單 :arrow_right:叫出功能選單\n" +
            "/開發者模式 :arrow_right:...",
            language='alias'))
    elif event.message.text.startswith("/角色"):
        prompt = event.message.text[3:]
        prompts._change_system(user_id=user_id, data=prompt)
        msg = TextMessage(text="設定完成!")
        line_bot_api.reply_message(event.reply_token, msg)

    elif event.message.text.startswith("/圖片"):
        prompt = event.message.text[3:]
        prompt += ", 4k"
        prompts._append(user_id=user_id, role="user", content=prompt)
        resp = openai.images.generate(
            prompt=prompt, n=1, size="512x512", model="dall-e-3")
        image_url = resp.data[0].url
        msg = ImageSendMessage(original_content_url=image_url,
                               preview_image_url=image_url)
        prompts._append(user_id=user_id, role="assistant", content=image_url)

    elif event.message.text.startswith("/清除"):
        prompt = event.message.text[3:]
        prompts._clear(user_id=user_id)
        msg = TextMessage(text="忘記了!")
    elif event.message.text.startswith("/開發者模式"):
        prompt = DEVELOPE_MODE_STRING
        prompts._append(user_id=user_id, role="user", content=prompt)
        print(
            f"after _append, message = {prompts._output_messages(user_id=user_id)}")
        resp = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=prompts._output_messages(user_id=user_id))
        msg = TextMessage(text=resp['choices'][0]['message']['content'])
        prompts._append(user_id=user_id,
                        role="assistant",
                        content=resp['choices'][0]['message']['content'])
    elif event.message.text.startswith("/影片總結"):
        url = event.message.text[5:]
        y = YT_handler(url)
        y.download()
        audio_file = open("audio.mp4", "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        prompt = SUMMARY_ASSISTANT_STRING + \
            " 下面是一個 Youtube 影片的部分字幕： \"\"\"{}\"\"\" \n\n請總結出這部影片的重點與一些細節，字數約 100 字左右".format(
                transcript["text"][:100])
        prompts._append(user_id=user_id, role="user", content=prompt)
        resp = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=prompts._output_messages(user_id=user_id))
        msg = TextMessage(text=resp['choices'][0]['message']['content'])
        prompts._append(user_id=user_id,
                        role="assistant",
                        content=resp['choices'][0]['message']['content'])

        line_bot_api.reply_message(event.reply_token, msg)
    else:
        prompts._append(user_id=user_id, role="user",
                        content=event.message.text)
        print("====for debug=======")
        print(
            f"after _append, message = {prompts._output_messages(user_id=user_id)}")
        resp = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=prompts._output_messages(user_id=user_id))
        msg = TextMessage(text=resp['choices'][0]['message']['content'])
        prompts._append(user_id=user_id,
                        role="assistant",
                        content=resp['choices'][0]['message']['content'])

    line_bot_api.reply_message(event.reply_token, msg)
    print(f"最新的messages: {prompts._output_messages(user_id=user_id)}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
