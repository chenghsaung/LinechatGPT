import os
import re
import openai
from flask import Flask, request, abort
from src.completion_handler import completion_heandler

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *

app = Flask(__name__)
user_id = os.getenv("OPENAI_API_KEY")

channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

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


button_template_message = ButtonsTemplate(
  thumbnail_image_url="https://i.imgur.com/i8tEmlY.jpg",
  title='哼！',
  text='選擇動作',
  ratio="1.51:1",
  image_size="cover",
  actions=[
    #                                PostbackTemplateAction 點擊選項後，
    #                                 除了文字會顯示在聊天室中，
    #                                 還回傳data中的資料，可
    #                                 此類透過 Postback event 處理。
    PostbackTemplateAction(label='填單', text='填單', data='action=buy&itemid=1'),
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
  if event.message.text == "Hi":
    line_bot_api.reply_message(
      event.reply_token,
      TemplateSendMessage(alt_text="Template Example",
                          template=button_template_message))
  elif event.message.text == "指令":
    line_bot_api.reply_message(
      event.reply_token,
      TextMessage(text="以下是機器人支援的指令:\n" +
                  "/角色 =>告訴機器人他是什麼角色，有助於產生更好的結果，例如:/system 你是一位專業股票分析師\n"))
  elif event.message.text.startswith("/角色"):
    prompt = event.message.text[7:]
    prompts._change_system(user_id=user_id, data=prompt)
    line_bot_api.reply_message(event.reply_token, TextMessage(text="角色設定完成!"))


  else:
    prompts._append(user_id=user_id, role="user", content=event.message.text)
    print("====for debug=======")
    print(
      f"after _append, message = {prompts._output_messages(user_id=user_id)}")
    resp = openai.ChatCompletion.create(
      model='gpt-3.5-turbo',
      messages=prompts._output_messages(user_id=user_id))

    prompts._append(user_id=user_id,
                    role="assistant",
                    content=resp['choices'][0]['message']['content'])
    line_bot_api.reply_message(
      event.reply_token,
      TextMessage(text=resp['choices'][0]['message']['content']))
  print(f"最新的messages: {prompts._output_messages(user_id=user_id)}")


if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True, port=8080)
