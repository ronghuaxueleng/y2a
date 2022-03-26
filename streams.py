import logging
from io import BufferedIOBase

from pytube import Stream as StreamBase, request

logger = logging.getLogger(__name__)


class Stream(StreamBase):
    def stream_to_raw(self, buffer: BufferedIOBase) -> None:
        """Write the media stream to buffer

        :rtype: io.BytesIO buffer
        """
        bytes_remaining = self.filesize
        logger.info(
            "downloading (%s total bytes) file to buffer", self.filesize,
        )

        request.stream(self.url)

        for chunk in request.stream(self.url):
            # reduce the (bytes) remainder by the length of the chunk.
            bytes_remaining -= len(chunk)
            # send to the on_progress callback.
            self.on_progress_raw(chunk, buffer, bytes_remaining)
        self.on_complete(None)

    def on_progress_raw(
        self, chunk: bytes, file_handler: BufferedIOBase, bytes_remaining: int
    ):
        """On progress callback function.

        This function writes the binary data to the file, then checks if an
        additional callback is defined in the monostate. This is exposed to
        allow things like displaying a progress bar.

        :param bytes chunk:
            Segment of media file binary data, not yet written to disk.
        :param file_handler:
            The file handle where the media is being written to.
        :type file_handler:
            :py:class:`io.BufferedWriter`
        :param int bytes_remaining:
            The delta between the total file size in bytes and amount already
            downloaded.

        :rtype: None

        """
        file_handler.write(chunk)
        logger.debug("download remaining: %s", bytes_remaining)
        if self._monostate.on_progress:
            self._monostate.on_progress(self, chunk, bytes_remaining)