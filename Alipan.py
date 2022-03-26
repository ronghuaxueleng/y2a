"""Aligo class"""
import json
import logging
from typing import Callable, Dict, Tuple

from aligo.apis.Audio import Audio
from aligo.apis.Copy import Copy
from aligo.apis.CustomShare import CustomShare
from aligo.apis.Download import Download
from aligo.apis.Drive import Drive
from aligo.apis.File import File
from aligo.apis.Move import Move
from aligo.apis.Other import Other
from aligo.apis.Recyclebin import Recyclebin
from aligo.apis.Search import Search
from aligo.apis.Share import Share
from aligo.apis.Star import Star
from aligo.apis.SyncFolder import SyncFolder
from aligo.apis.Update import Update
from aligo.apis.Video import Video
from typing_extensions import NoReturn

from Create import Create
from aligo import aligo_config_folder


class Aligo(
    Audio,
    Video,
    Copy,
    Create,
    Drive,
    File,
    Move,
    Download,
    Recyclebin,
    Search,
    Share,
    CustomShare,
    Star,
    Update,
    Other,
    SyncFolder,
):
    """阿里云盘"""

    def __init__(
            self,
            name: str = 'aligo',
            refresh_token: str = None,
            show: Callable[[str], NoReturn] = None,
            level: int = logging.DEBUG,
            use_aria2: bool = False,
            proxies: Dict = None,
            port: int = None,
            email: Tuple[str, str] = None,
    ):
        """
        Aligo
        :param name: (可选, 默认: aligo) 配置文件名称, 便于使用不同配置文件进行身份验证
        :param refresh_token:
        :param show: (可选) 显示二维码的函数
        :param level: (可选) 控制控制台输出
        :param use_aria2: [bool] 是否使用 aria2 下载
        :param proxies: (可选) 自定义代理 [proxies={"https":"localhost:10809"}],支持 http 和 socks5（具体参考requests库的用法）
        :param port: (可选) 开启 http server 端口，用于网页端扫码登录. 提供此值时，将不再弹出或打印二维码
        :param email: (可选) 发送扫码登录邮件 ("接收邮件的邮箱地址", "防伪字符串"). 提供此值时，将不再弹出或打印二维码
            关于防伪字符串: 为了方便大家使用, aligo 自带公开邮箱, 省去邮箱配置的麻烦.
                        所以收到登录邮件后, 一定要对比确认防伪字符串和你设置一致才可扫码登录, 否则将导致: 包括但不限于云盘文件泄露.
            关于防伪字符串: 为了方便大家使用, aligo 自带公开邮箱, 省去邮箱配置的麻烦.
                        所以收到登录邮件后, 一定要对比确认防伪字符串和你设置一致才可扫码登录, 否则将导致: 包括但不限于云盘文件泄露.
            关于防伪字符串: 为了方便大家使用, aligo 自带公开邮箱, 省去邮箱配置的麻烦.
                        所以收到登录邮件后, 一定要对比确认防伪字符串和你设置一致才可扫码登录, 否则将导致: 包括但不限于云盘文件泄露.

        level, use_aria2, proxies, port, email 可以通过 配置文件 配置默认值，在 <用户家目录>/.aligo/config.json5 中
        ```json5
        {
          "level": 10,
          "use_aria2": false,
          "proxies": {
            "https": "http://localhost:10809",
            // "https": "socks5://localhost:10808", # 不支持注释，写的时候删掉
          },
          "port": 8080,
          "email": ["邮箱地址", "防伪字符串"]
        }
        ```
        """
        # aligo_config_folder = Path().joinpath('.aligo')
        # aligo_config_folder.mkdir(parents=True, exist_ok=True)
        config = aligo_config_folder / 'config.json5'
        if config.exists():
            config = json.loads(config.open().read())
            if level == logging.DEBUG and 'level' in config:
                level = config.get('level')
            if not use_aria2:
                use_aria2 = config.get('use_aria2')
            if proxies is None:
                proxies = config.get('proxies')
            if port is None:
                port = config.get('port')
            if email is None:
                email = config.get('email')

        super().__init__(
            name,
            refresh_token,
            show,
            level,
            use_aria2,
            proxies,
            port,
            email,
        )
