import re
from rest_framework import serializers
from django_redis import get_redis_connection

from goods.models import SKU
from .models import *
from rest_framework_jwt.settings import api_settings
from celery_tasks.email.tasks import send_email_active
from utils import tjws
from django_redis import get_redis_connection
from rest_framework_jwt.views import ObtainJSONWebToken


class UserSerializers(serializers.Serializer):
    """用户序列器，用于注册"""
    id  =serializers.IntegerField(read_only=True)

    username= serializers.CharField(max_length=20,min_length=5,error_messages={
        "min_length":"用户名为5-20个字符",
        "max_length":'用户名为5-20个字符'
    })
    password = serializers.CharField(max_length=20,min_length=8,error_messages={
        "min_length":"密码为8-20字符",
        "max_length":"密码为8-20个字符"
    },write_only=True)
    mobile =serializers.CharField()
    password2 =serializers.CharField(write_only=True)
    sms_code =serializers.CharField(write_only=True)
    allow= serializers.CharField(write_only=True)
    token =serializers.CharField(read_only=True)

    def validate_username(self,value):
        """用户名验证"""
        if User.objects.filter(username =value).count()>0:
            raise serializers.ValidationError("用户名已存在!")
        return value

    def validate_mobile(self,value):
        if not re.match('^1[3-9]\d{9}$',value):
            raise serializers.ValidationError("手机号码不合法")
        return value


    def validate_allow(self,value):
        if not value:
            raise serializers.ValidationError("必须同意协议")
        return value

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            return serializers.ValidationError("两次密码不一致")

        redis_cli = get_redis_connection("sms_code")

        sms="sms_code"+attrs.get('mobile')
        sms_code_redis = redis_cli.get(sms)

        if not sms_code_redis:
            raise  serializers.ValidationError("验证码已经过期")

        redis_cli.delete(sms)
        sms_code_redis = sms_code_redis.decode()
        sms_code_re= attrs.get('sms_code')

        if sms_code_redis != sms_code_re:
            raise  serializers.ValidationError("验证码输入错误")

        return attrs


    def create(self, validated_data):
        user= User()
        user.username = validated_data.get('username')
        user.mobile = validated_data.get('mobile')
        user.set_password(validated_data.get('mobile'))
        user.save()

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token
        return user


class UserDetailSerializers(serializers.ModelSerializer):
    """详情序列化"""
    class Meta:
        model= User
        fields= ['id','username','mobile','email','email_active']


class EmailSerializers(serializers.ModelSerializer):
    """绑定邮箱"""
    class Meta:
        model = User
        fields=('id','email')

    def update(self, instance, validated_data):
        """重写update方法"""

        email= validated_data.get('email')
        instance.email =email
        instance.save()

        verify_email=instance.generate_email_verify()
        send_email_active.delay(email,verify_email)
        return instance


class EmailActiveSerializers(serializers.Serializer):
    """激活邮箱"""
    token = serializers.CharField(max_length=128)

    # def validate(self, attrs):
    #     print("11111")
    #     data= tjws.loads(attrs.get("token"),60*60)
    #     if data is None:
    #         raise serializers.ValidationError("邮箱验证已失效")
    #     return data.get('user_id')
    #
    # def create(self, validated_data):
    #     print("22222")
    #
    #     user = User.objects.get(pk = validated_data.get('token'))
    #     print(user)
    #     user.email_active= True
    #
    #     user.save()
    #     return user


class AddressSerializers(serializers.ModelSerializer):
    """收货地址的序列化器"""
    province_id = serializers.IntegerField(required=True)
    city_id = serializers.IntegerField(required=True)
    district_id =serializers.IntegerField(required=True)

    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Address
        exclude =['user','create_time','update_time','is_deleted']

    def validate_mobile(self,value):
        if not re.match("^1[3-9]\d{9}$",value):
            raise serializers.ValidationError("手机不合法")
        return value

    def create(self, validated_data):
        validated_data['user']=self.context['request'].user
        return super().create(validated_data)


class BrwserHistorySerializer(serializers.Serializer):
    sku_id = serializers.IntegerField()

    def validated_sku_id(self,value):
        count = SKU.objects.filter(pk =value).count()
        if count <= 0:
            raise serializers.ValidationError("该商品不存在")
        return value

    def create(self, validated_data):
        user_id = self.context['request'].user.id
        sku_id = validated_data.get('sku_id')
        # 创建reds链接
        redis_cli = get_redis_connection('history')
        # 开启管道
        pl = redis_cli.pipeline()
        # 删除存在的
        pl.lrem('history_%s'% user_id,0,sku_id)
        # 左侧插入数据包
        pl.lpush('history_%s'%user_id,sku_id)
        # 限制条数为５条
        pl.ltrim("history_%s" % user_id, 0,4)

        pl.execute()

        return validated_data