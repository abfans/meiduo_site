from rest_framework import serializers
from django_redis import get_redis_connection
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from .models import OauthUser
from users.models import User
from django.conf import settings
from .units import OAuthQQ
from .models import OauthUser


class QoauthSerializers(serializers.Serializer):
    """通过qq绑定用户"""
    mobile = serializers.CharField(max_length=11)
    password =serializers.CharField(write_only=True)
    sms_code = serializers.CharField(write_only=True)
    access_token =serializers.CharField(write_only=True)

    def validate(self,attrs):
        """验证信息"""
        """
        验证短信验证码
        """
        sms_code = attrs.get('sms_code')
        mobile = attrs.get('mobile')
        access_token = attrs.get('access_token')

        redis_cli = get_redis_connection("sms_code")
        # 从redis中取出验证码和接受的验证码校验
        try:
            redis_code = redis_cli.get('sms_code'+mobile).decode()
        except:
            raise serializers.ValidationError("数据错误")

        if redis_code != sms_code:
            raise serializers.ValidationError("短信验证码错误")

        # 手机号验证
        try:
            user = User.objects.get(mobile = mobile)
        except:
            pass
        else:
            if not user.check_password(attrs.get('password')):
                raise serializers.ValidationError('密码错误')

            attrs['user'] = user

        openid = OAuthQQ.check_openid_token(access_token)
        print(openid)
        if not openid:
            raise serializers.ValidationError('无效的access_token')
        attrs['openid'] = openid

        return attrs

    def create(self, validated_data):
        """创建用户或者保存用户ＱＱ关系表"""
        user  =  validated_data.get('user')
        openid = validated_data.get('openid')

        if not user:
            # 手机号没有注册，创建用户
            user = User()
            user.mobile = validated_data.get('mobile')
            user.username =validated_data.get('mobile')
            user.set_password(validated_data.get('password'))
            user.save()

        qq_user = OauthUser()
        qq_user.openid= openid
        qq_user.user = user
        qq_user.save()

        return qq_user
