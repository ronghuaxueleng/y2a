import io

from Youtube import YouTube

proxies = {
    "http": "http://localhost:1080",
    "https": "http://localhost:1080",
}
# proxies = {}

buffer = io.RawIOBase()
url = YouTube("http://youtube.com/watch?v=9bZkp7q19f0", proxies=proxies)
print(url.title)
video = url.streams.filter(only_video=True).order_by('resolution').last()
print(video)
# stream.download("D://桌面", "filename", "filename_prefix")
# video = url.streams.get_by_itag(18)
video.stream_to_buffer(buffer)
buffer.seek(0)
data = buffer.read()
print(data)
