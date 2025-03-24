"""
The file that contains the class that handle images endpoint
"""

import os
import tempfile
import uuid
from typing import Union, List
from fastapi import Response, UploadFile
from display_tty import Disp, TOML_CONF, FILE_DESCRIPTOR, SAVE_TO_FILE, FILE_NAME
from . import constants as CONST
from .runtime_data import RuntimeData

class ImageHandler:
    """
    The class that handle images endpoint
    """
    def __init__(self, runtime_data: RuntimeData, success: int = 0, error: int = 84, debug: bool = False) -> None:
        """
        The constructor of the Bonus class
        """
        self.debug: bool = debug
        self.success: int = success
        self.error: int = error
        self.runtime_data_initialised: RuntimeData = runtime_data
        self.disp: Disp = Disp(
            TOML_CONF,
            SAVE_TO_FILE,
            FILE_NAME,
            FILE_DESCRIPTOR,
            debug=self.debug,
            logger=self.__class__.__name__
        )

    async def upload_image(self, bucket_name: str, title: str, file: UploadFile, key_name: str) -> Union[str, Response]:
        """
        A generic function to upload an image
        """
        # Vérify if the bucket exist, if not the code create it
        self.disp.log_debug(f"Given file={file}", title)
        buckets_list: Union[List[str], int] = self.runtime_data_initialised.bucket_link.get_bucket_names()
        if buckets_list == self.error or bucket_name not in buckets_list:
            creation_status: int = self.runtime_data_initialised.bucket_link.create_bucket(
                bucket_name
            )
            if creation_status != self.success:
                return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                    title=title
                )
        filename = file.filename
        self.disp.log_debug(f"File={file}", title)
        extension = "."
        extension += filename.split(".")[-1]
        self.disp.log_debug(f"Extension={extension}", title)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            file_content = await file.read()
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        # Upload the file in the MiniIO S3
        unique_key_name: str = f"{uuid.uuid4().hex}-{key_name}"
        unique_key_name += extension
        upload_status: int = self.runtime_data_initialised.bucket_link.upload_file(
            bucket_name=bucket_name,
            file_path=temp_file_path,
            key_name=unique_key_name
        )
        if upload_status != self.success:
            os.remove(temp_file_path)
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                    title=title
                )
        os.remove(temp_file_path)
        return f"{CONST.MINIO_HOST}:{CONST.MINIO_PORT}/{bucket_name}/{unique_key_name}"
