from django.contrib.auth.backends import ModelBackend
from rest_framework.response import Response

from .models import User
import re


def jwt_response_payload_handler(token,user=None,request =None):
    """自定义jwt返回数据"""
    return {
        "token":token,
        "user_id":user.id,
        "username":user.username
    }


class MyAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 根据username查询对象
        if re.match(r'^1[3-9]\d{9}$', username):
            # 当前为手机号
            try:
                user = User.objects.get(mobile=username)
            except User.DoesNotExist:
                return None
        else:
            # 当前为用户名
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None

        if user is not None and user.check_password(password):
            return user
