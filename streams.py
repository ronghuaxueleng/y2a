import io
import logging
from io import BytesIO

import requests
from pytube import Stream as StreamBase

logger = logging.getLogger(__name__)


class Stream(StreamBase):
    def stream_to_raw(self, proxies) -> BytesIO:
        response = requests.get(self.url, proxies=proxies)
        return io.BytesIO(response.content)
