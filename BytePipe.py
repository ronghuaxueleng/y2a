import io
from threading import Thread
from pytube import YouTube
from ftplib import FTP, error_temp
from queue import Queue


class BytePipe:

    def __init__(self, size: int):
        self.q = Queue()
        self.size = size
        self.bytes_read = 0

    def read(self, blocksize: int):
        if self.bytes_read == self.size:
            return False

        chunk = self.q.get(block=True)
        self.bytes_read += len(chunk)
        return chunk

    def write(self, chunk: bytes):
        self.q.put(chunk, block=True)


if __name__ == "__main__":
    ftp = FTP("127.0.0.1")
    ftp.login(user="anon")

    gangnam = YouTube('https://www.youtube.com/watch?v=9bZkp7q19f0')
    stream = gangnam.streams.first()

    pipe = BytePipe(stream.filesize)
    stream.on_progress = lambda chunk, fh, br: pipe.write(chunk)

    with io.BytesIO() as buffer:
        t = Thread(target=stream.stream_to_buffer, args=(buffer,))
        t.start()

        while True:
            try:
                ftp.storbinary("STOR file.txt", pipe, blocksize=9437184)
                break
            except error_temp as e:
                print("temp error, retrying...")

        t.join()
