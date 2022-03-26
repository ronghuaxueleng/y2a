import hashlib
import io
import math
from typing import Union

import requests
from aligo.apis.Create import Create as BaseCreate
from aligo.core import *
from aligo.core.Config import *
from aligo.request import *
from aligo.response import *
from aligo.types import *
from aligo.types.Enum import *
from Youtube import YouTube
from requests.adapters import HTTPAdapter
from tqdm import tqdm


class Create(BaseCreate):
    _UPLOAD_CHUNK_SIZE: int = None
    __UPLOAD_CHUNK_SIZE: int = 10485760  # 10 MB

    def complete_file(self, body: CompleteFileRequest) -> BaseFile:
        """
        完成文件上传 当文件上传完成时调用
        :param body: [CompleteFileRequest]
        :return: [BaseFile]

        :Example:
        >>> from aligo import Aligo
        >>> ali = Aligo()
        >>> result = ali.complete_file(CompleteFileRequest(file_id='file_id', part_info_list=[UploadPartInfo(part_number=1)]))
        >>> print(result.file_id)
        """
        response = self._post(V2_FILE_COMPLETE, body=body)
        return self._result(response, BaseFile)

    @staticmethod
    def _get_part_info_list(file_size: int):
        """根据文件大小, 返回 part_info_list """
        # 以10MB为一块: 10485760
        return [UploadPartInfo(part_number=i) for i in range(1, math.ceil(file_size / Create.__UPLOAD_CHUNK_SIZE) + 1)]

    def _pre_hash(self, buffer: io.BufferedIOBase, file_size: int, name: str, parent_file_id='root', drive_id=None,
                  check_name_mode: CheckNameMode = 'auto_rename') -> CreateFileResponse:
        pre_hash = hashlib.sha1(buffer.read(1024)).hexdigest()
        body = CreateFileRequest(
            drive_id=drive_id,
            part_info_list=self._get_part_info_list(file_size),
            parent_file_id=parent_file_id,
            name=name,
            type='file',
            check_name_mode=check_name_mode,
            size=file_size,
            pre_hash=pre_hash
        )
        response = self._post(ADRIVE_V2_FILE_CREATEWITHFOLDERS, body=body)
        part_info = self._result(response, CreateFileResponse, [201, 409])
        return part_info

    def _put_data(self, buffer: any, part_info: CreateFileResponse, file_size: int) -> Union[BaseFile, Null]:
        """上传数据"""
        # llen = len(part_info.part_info_list)
        progress_bar = tqdm(total=file_size, unit='B', unit_scale=True, colour='#21d789')
        for i, e in enumerate(part_info.part_info_list):
            ss = requests.session()
            ss.mount('https://', HTTPAdapter(max_retries=5))
            data = buffer.read(Create.__UPLOAD_CHUNK_SIZE)
            r = ss.put(data=data, url=e.upload_url)
            if r.status_code == 403:
                part_info = self.get_upload_url(GetUploadUrlRequest(
                    drive_id=part_info.drive_id,
                    file_id=part_info.file_id,
                    upload_id=part_info.upload_id,
                    part_info_list=[UploadPartInfo(part_number=i.part_number) for i in part_info.part_info_list]
                ))
                ss.put(data=data, url=e.upload_url)
            progress_bar.update(len(data))

        progress_bar.close()

        # complete
        complete = self.complete_file(CompleteFileRequest(
            drive_id=part_info.drive_id,
            file_id=part_info.file_id,
            upload_id=part_info.upload_id,
            part_info_list=part_info.part_info_list
        ))
        self._auth.log.info(f'文件上传完成 {part_info.file_name}')
        return complete

    def upload_file_from_youtube(
            self,
            url: str,
            parent_file_id: str = 'root',
            name: str = None,
            drive_id: str = None,
            check_name_mode: CheckNameMode = "auto_rename",
            proxies=None
    ) -> Union[BaseFile, CreateFileResponse]:
        """
        从YouTube下载视频上传文件
        :param url: [str] 文件路径
        :param parent_file_id: [str] 父文件夹id
        :param name: [str] 文件名
        :param drive_id: [str] 父文件夹所在的网盘id
        :param check_name_mode: [CheckNameMode] 文件名检查模式, 默认为auto_rename
        :param proxies: 代理
        :return: [Union[BaseFile, CreateFileResponse]]

        :Example:
        >>> from aligo import Aligo
        >>> ali = Aligo()
        >>> up_file = ali.upload_file_from_youtube('https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'root')
        >>> print(up_file)
        """
        yt = YouTube(url, proxies=proxies)
        video = yt.streams.filter(only_video=True).order_by('resolution').last()
        title = yt.title

        self._auth.log.info(f'开始上传文件 {url}[{title}]')

        if name is None:
            name = f'{title.replace(" ", "_")}.mp4'

        if drive_id is None:
            drive_id = self.default_drive_id

        file_size = video.filesize
        buffer = video.stream_to_raw(proxies)

        # 动态调整 _UPLOAD_CHUNK_SIZE
        if Create._UPLOAD_CHUNK_SIZE is None:
            if file_size < 104857600000:  # (1024 * 1024 * 10) * 10000
                Create.__UPLOAD_CHUNK_SIZE = 10485760  # (1024 * 1024 * 10) => 10 MB
            else:
                Create.__UPLOAD_CHUNK_SIZE = 268435456  # 256 MB
        else:
            if file_size < Create._UPLOAD_CHUNK_SIZE * 10000:
                Create.__UPLOAD_CHUNK_SIZE = Create._UPLOAD_CHUNK_SIZE
            else:
                Create.__UPLOAD_CHUNK_SIZE = 268435456  # 256 MB

        part_info = self._pre_hash(buffer=buffer, file_size=file_size, name=name,
                                   parent_file_id=parent_file_id, drive_id=drive_id,
                                   check_name_mode=check_name_mode)
        # exists=True
        if part_info.exist:
            self._auth.log.warning(f'文件已存在, 跳过 {url}[{title}] {part_info.file_id}')
            # return self.get_file(GetFileRequest(file_id=part_info.file_id))
            return part_info

        return self._put_data(buffer, part_info, file_size)
