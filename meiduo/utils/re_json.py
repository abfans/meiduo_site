import base64
import pickle


"""
pickle.dumps() 将python数据序列化为bytes类型
pickle.loads() 将bytes类型数据反序列化为python的数据类型
base64.b64encode() 将bytes类型数据进行base64编码，返回编码后的bytes类型
base64.b64deocde() 将base64编码的bytes类型进行解码，返回解码后的bytes类型
"""
def loads(my_str):
    """把字节转化为字典"""
    bs = my_str.encode() # 把１６进制字典转成为字符串
    bs64 =base64.b64decode(bs)   # 将base64编码的bytes类型进行解码
    return pickle.loads(bs64)


def dumps(my_dict):
    """将字典转为字节"""
    bs = pickle.dumps(my_dict)
    bs64 = base64.b64encode(bs)
    return bs64.decode()