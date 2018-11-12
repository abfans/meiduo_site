from rest_framework.response import Response
from rest_framework.views import APIView
from django_redis import get_redis_connection
from .serializers import CartsSerializer,CartListSerializer,CartDeleteSerializer,CartAllSerializer
from utils import re_json
from goods.models import SKU

# Create your views here.


class CartView(APIView):
    def perform_authentication(self, request):
        """"""
        pass

    """购物车功能"""
    def post(self,request):
        try:
            user= request.user
        except Exception:
            user =None

        serializer = CartsSerializer(data=request.data)

        if  not serializer.is_valid():
            raise serializer.errors

        sku_id =serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        is_select = serializer.validated_data.get('selected')
        response = Response(serializer.data, status=201)

        if user is not None:
            # 如果用户登陆了，则将购物车保存到redis中
            redis_cli = get_redis_connection('cart')
            redis_cli.hset('cart_%s' %user.id,sku_id,count)
            redis_cli.sadd('cart_selected_%d'%user.id,sku_id)

        else:
            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = re_json.loads(cart)
            else:
                cart ={}

            if sku_id in cart:
                cart_count =int(cart[sku_id]['count'])
            else:
                cart_count =0

            cart[sku_id] = {
                "count":cart_count+count,
                "selected":is_select
            }
            cookile＿cart=re_json.dumps(cart)
            response.set_cookie('cart',cookile＿cart,max_age=60*60*24)

        return response

    def get(self,request):
        try:
            user =self.request.user
        except Exception:
            user =None

        if user is not None:
            redis_cli = get_redis_connection("cart")
            redis_cart = redis_cli.hgetall('cart_%s'% user.id,)
            redis_select = redis_cli.smembers('cart_selected_%s' % user.id)
            cart={}
            # 遍历数据库，取出数据，构造字典
            for sku_id,count in redis_cart.items():
                cart[int(sku_id)] ={
                    "count":count,
                    "selected":sku_id in redis_select
                }
        else:
            cart = request.COOKIES.get('cart')
            if cart:
                cart =re_json.loads(cart)
            else:
                cart={}

        skus =SKU.objects.filter(id__in=cart.keys())
        # 给查询集增加属性，构造返回结果
        for sku in skus:
            sku.count= cart[sku.id]['count']
            sku.selected =cart[sku.id]['selected']

        serializer = CartListSerializer(skus,many=True)
        return Response(serializer.data)

    def put(self,request):

        try:
            user = self.request.user
        except:
            user = None

        serializer = CartsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        is_select = serializer.validated_data.get('selected')

        response = Response(serializer.data, status=201)
        if user is not None and user.is_authenticated:
            # 如果用户登陆了，则将购物车保存到redis中
            redis_cli = get_redis_connection('cart')

            redis_cli.hset('cart_%s' % user.id, sku_id, count)
            if is_select:
                # 选中就修改
                redis_cli.sadd('cart_selected_%d' % user.id, sku_id)
            else:
                # 未选中就从redis删除
                redis_cli.srem('cart_selected_%d' % user.id, sku_id)
        else:
            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = re_json.loads(cart)
            else:
                cart = {}

            cart[sku_id] = {
                "count": count,
                "selected": is_select
            }
            cookile＿cart = re_json.dumps(cart)
            response.set_cookie('cart', cookile＿cart, max_age=60 * 60 * 24)

        return response

    def delete(self,request):
        """从购物车中删除"""
        serializer = CartDeleteSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)

        sku_id = serializer.validated_data.get('sku_id')
        try:
            user =self.request.user
        except:
            user = None
        response = Response(status=204)
        if user is not None:
            redis_cli = get_redis_connection("cart")
            pl = redis_cli.pipeline()
            pl.hdel('cart_%s'%user.id,sku_id)
            pl.srem('cart_selected_%s' % user.id, sku_id)
            pl.execute()

        else:
            cart = request.COOKIES.get('cart')

            if cart is not None:
                cart =re_json.loads(cart)
                if sku_id in cart:
                    del cart[sku_id]
                cookie_cart = re_json.dumps(cart)
                response.set_cookie('cart',cookie_cart,24*60*60)

        return response


class CartAllvie(APIView):
    def perform_authentication(self, request):
        pass

    def put(self,request):
        try:
            user = request.user
        except:
            user = None

        serializer = CartAllSerializer(data =request.data)
        serializer.is_valid(raise_exception=True)

        selected =serializer.validated_data.get('selected')
        response =Response({"message":"ok"})
        if user is not None and user.is_authenticated:
            key1 = 'cart_%s' %user.id
            key2 = 'cart_selected_%S' %user.id
            redis_cli = get_redis_connection("cart")
            redis_keys=redis_cli.hkeys(key1)
            if selected:
                redis_cli.sadd(key2,*redis_keys)
            else:
                redis_cli.srem(key2,*redis_keys)
        else:
            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = re_json.loads(cart)
            else:
                cart={}
            for data in cart.values():
                data['selected']=selected

            cart_cookie = re_json.dumps(cart)
            response.set_cookie('cart',cart_cookie,60*60*24)
        return response
