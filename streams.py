import logging

import requests
from pytube import Stream as StreamBase

logger = logging.getLogger(__name__)


class Stream(StreamBase):
    def stream_to_raw(self, proxies) -> None:
        response = requests.get(self.url, proxies=proxies, stream=True)
        return response.raw
