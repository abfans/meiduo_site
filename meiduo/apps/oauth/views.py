from django.shortcuts import render
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.units import generate_jwt_token
from .models import OauthUser
from .units import OAuthQQ
from .serialers import QoauthSerializers
from utils.units import generate_jwt_token
from utils.cookie_merge_user_cart import cookie_merge_cart

# Create your views here.
class QOauth(APIView):
    """qq授权登录类"""
    def get(self,request):
        next = request.query_params.get('next')
        oauth = OAuthQQ(state=next)
        login_url = oauth.get_qq_login_url()
        return Response({"login_url":login_url})


class QoauthUserView(APIView):
    def get(self,request):
        """根据code获openid"""

        code = request.query_params.get('code')
        if not code:
            return Response({"message":"缺少code"})

        oauth = OAuthQQ()
        try:
            # 生成openid
            token = oauth.get_access_token(code)
            openid = oauth.get_openid(token)
        except:
            return Response({"message":"服务器异常"})

        # 是否为第一次用ｑｑ授权登陆
        try:
            oauth_user = OauthUser.objects.get(openid=openid)
        except OauthUser.DoesNotExist:
            # 第一次登陆，讲openid加密返回
            access_token= oauth.generate_openid_token(openid)
            return Response({
                "access_token":access_token,
            })
        else:
            response =Response({
                 "token": generate_jwt_token(oauth_user.user),
                 "username": oauth_user.user.username,
                 "user_id": oauth_user.user.id

            })
            response =cookie_merge_cart(request,oauth_user.user,response)

            return response

    def post(self,request):
        # 接受参数并序列化
        oauth = QoauthSerializers(data=request.data)
        # 校验参数
        if not oauth.is_valid():
            return Response({"message":oauth.errors})

        qquser=oauth.save()
        response = Response({
            "token":generate_jwt_token(qquser.user),
            "user_id":qquser.user.id,
            "username":qquser.user.username,
        })

        # response =cookie_merge_cart(request,qquser.user,response)
        return response
