# import youtube_transcript_api
import math
from pytube import YouTube


class YT_handler:
    def __init__(self, url):
        self.url = url
        self.yt = YouTube(url, on_progress_callback=self.onProgress)

    def onProgress(self, stream, chunk, remains):
        total = stream.filesize                     # 取得完整尺寸
        percent = (total-remains) / total * 100     # 減去剩餘尺寸 ( 剩餘尺寸會抓取存取的檔案大小 )
        print(f'下載中… {percent:05.2f}', end='\r')  # 顯示進度，\r 表示不換行，在同一行更新

    def download(self):
        video = self.yt.streams.filter(file_extension='mp4').first()
        video.download(filename="audio.mp4")


if __name__ == '__main__':
    y = YT_handler(
        "https://www.youtube.com/watch?v=9f0Ml-e1Zos&ab_channel=%E6%9D%B1%E6%A3%AE%E6%96%B0%E8%81%9ECH51")
    y.download()
