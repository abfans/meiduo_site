from _decimal import Decimal
from rest_framework.generics import CreateAPIView
from .seriallizers import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_redis import get_redis_connection

# Create your views here.
from goods.models import SKU
from .seriallizers import SaveOrderSerializer


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        """从数据库中读取加入购物车且被选中的商品"""
        user = request.user
        key = 'cart_%s'%user.id
        key1 = 'cart_selected_%s'%user.id
        redis_cli = get_redis_connection('cart')
        reds_cart = redis_cli.hgetall(key)
        redis_select  = redis_cli.smembers(key1)
        redis_select = [int(id) for id in redis_select]

        skus = SKU.objects.filter(id__in=redis_select)

        for sku in skus:
            sku.count = redis_cli.hget(key,sku.id)
        freight = Decimal('10.00')

        serializer = OrderSettlementSerializer({"freight":freight,"skus":skus})

        return Response(serializer.data)

class OrderView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SaveOrderSerializer