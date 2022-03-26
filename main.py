"""快速入门"""
from Alipan import Aligo

if __name__ == '__main__':
    proxies = {
        "http": "http://localhost:1080",
        "https": "http://localhost:1080",
    }

    ali = Aligo()
    up_file = ali.upload_file_from_youtube_with_proxy('http://youtube.com/watch?v=9bZkp7q19f0', 'root', proxies)
    print(up_file)
