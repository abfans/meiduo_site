from django.conf import settings
from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.utils.deconstruct import deconstructible


@deconstructible
class FastDFSStorage(Storage):
    """自定义文件上传类"""
    def __init__(self,client_conf =None ,storage_url = None):
        self.client_conf= client_conf or settings.FDFS_CLIENT_CONF
        self.storage_url = storage_url or settings.FDFS_URL

    def open(self, name, mode='rb'):
        pass


    def save(self, name, content, max_length=None):
        client = Fdfs_client(self.client_conf)
        ret  = client.upload_by_buffer(content.read())

        if ret['Status'] != 'Upload successed.':
            raise  Exception("文件上传失败")
        return ret['Remote file_id']

    def url(self, name):
        # 返回绝对路径
        return self.storage_url +name

    def exists(self, name):
        return False