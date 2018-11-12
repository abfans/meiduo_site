import random

from django.shortcuts import render

# Create your views here.
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from django_redis import get_redis_connection
from rest_framework import serializers

from users.models import User
from .constans import *
from celery_tasks.sms.tasks import send_sms_code


class SMSCodeView(APIView):
    def get(self,request,mobile):

        redis_cli =get_redis_connection('sms_code')
        # 验证是否发送过验证码
        if redis_cli.get('sms_flag'+mobile):
            raise serializers.ValidationError("请不要重发发送")


        code = random.randint(1,999999)
        sms_code = "%06d"% code
        # 创建redis管道，只交互一次
        redis_pipeline = redis_cli.pipeline()
        redis_pipeline.setex("sms_code"+mobile,SMS_CODE_EXPIRE,sms_code)
        redis_pipeline.setex('sms_flag'+mobile,SMS_FLAG_EXPIRE,1)
        redis_pipeline.execute()

        send_sms_code.delay(mobile,sms_code,SMS_CODE_EXPIRE/60,1)

        return Response({"message":"ok"})


class MobilesView(APIView):
    """手机号验证"""
    def get(self,request,mobile):

        # 丛书据库中获取与该手机号匹配的数据的数量
        count = User.objects.filter(mobile=mobile).count()
        data = {
            "mobile":mobile,
            "count":count
        }
        return Response(data)



class UsernamesView(APIView):
    """手机号验证"""
    def get(self,request,username):

        # 丛书据库中获取与该手机号匹配的数据的数量
        count = User.objects.filter(username= username).count()
        data = {
            "username":username,
            "count":count
        }
        return Response(data)