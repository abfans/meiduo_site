from fdfs_client.client import Fdfs_client

if __name__ == '__main__':
    # 加载配置文件
    client = Fdfs_client('client.conf')

    ret =client.upload_by_file('/home/python/Desktop/1.png')
    print(ret)