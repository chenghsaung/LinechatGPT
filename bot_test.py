import openai
import os
from src.youtube_handler import YT_handler
openai.api_key = "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"


# completion = openai.ChatCompletion.create(
#     model='gpt-3.5-turbo',
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "Who won the world series in 2020?"},
#         {"role": "assistant",
#             "content": "The Los Angeles Dodgers won the World Series in 2020."},
#         {"role": "user", "content": "Where was it played?"}
#     ],
#     temperature=0
# )

# response = openai.Image.create(
#     prompt="a white siamese cat",
#     n=1,
#     size="1024x1024"
# )
# image_url = response['data'][0]['url']
# print(image_url)
audio_file = open("audio.mp4", "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file)
file = open('./subtitle.txt', 'w',encoding="utf-8")
file.write(transcript["text"])