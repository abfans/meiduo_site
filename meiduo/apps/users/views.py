from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView,RetrieveAPIView,UpdateAPIView,GenericAPIView,ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from users.models import User, Address
from utils import tjws
from .serializers import *
from goods.serializers import SKUSerializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.views import ObtainJSONWebToken
from utils.cookie_merge_user_cart import cookie_merge_cart



# Create your views here.
class UsersView(CreateAPIView):
    """注册"""
    serializer_class = UserSerializers


class UserView(RetrieveAPIView):
    serializer_class = UserDetailSerializers
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user  # 重写get_object方法


class EmailsView(UpdateAPIView):
    """绑定邮箱"""
    serializer_class = EmailSerializers
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class LoginView(ObtainJSONWebToken):
    def post(self, request, *args, **kwargs):
        response =super().post(request, *args, **kwargs)
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            response = cookie_merge_cart(request, user, response)
        return response



class EmailVerificationView(APIView):
    def get(self,request):
        # serializer= EmailActiveSerializers(data =request.query_params)
        data = request.query_params.get('token')
        user_id = tjws.loads(data,60*60).get('user_id')
        # if not serializer.is_valid():
        #     return Response({'message': "链接信息无效"},status=404)

        user =User.objects.get( pk= user_id)
        user.email_active =True
        user.save()
        return Response({"message": "OK"})


class AddressViewsets(ModelViewSet):

    serializer_class = AddressSerializers
    permission_classes = [IsAuthenticated]

    # 自定义查询范围
    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    # 重写查询方法
    def list(self, request, *args, **kwargs):
        address = self.get_queryset()
        serializer =self.get_serializer(address,many=True)

        return Response({
            "user_id":request.user.id,
            'default_address_id': request.user.default_address_id,
            'limit': 5,
            'addresses': serializer.data # [{},{},...]
        })

    #　重写destroy方法实现逻辑删除
    def destroy(self, request, *args, **kwargs):
        address =self.get_object()
        address.is_deleted= True
        address.save()

        return Response(status=204)


    @action(methods=['put'],detail=True)
    def title(self,request,pk):
        title =request.data.get('title')
        address =self.get_object()
        address.title = title
        address.save()

        return Response({"message":"ok"})

    @action(methods=['put'], detail=True)
    def status(self,request, pk):
        user =request.user
        user.default_address_id = pk
        user.save

        return Response({"message": "ok"})


class BrwserHistoryView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SKUSerializers
        else:
            return BrwserHistorySerializer

    def get_queryset(self):
        redis_cli =get_redis_connection("history")
        indexs = redis_cli.lrange("history_%d" % self.request.user.id, 0, 4)
        sku_list = []
        for index in indexs:
            sku= SKU.objects.get(pk=int(index))
            sku_list.append(sku)

        return sku_list