"""快速入门"""
from Alipan import Aligo

if __name__ == '__main__':
    # proxies = {
    #     "http": "http://localhost:1080",
    #     "https": "http://localhost:1080",
    # }

    proxies = {}

    ali = Aligo(refresh_token="d816542f503f4d8f967fc4cba2c086e7")
    up_file = ali.upload_file_from_youtube('http://youtube.com/watch?v=9bZkp7q19f0', proxies=proxies)
    ali.upload_file()
    print(up_file)
