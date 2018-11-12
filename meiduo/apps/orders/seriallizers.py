from rest_framework import serializers
from goods.models import  SKU
from users.models import Address
from django_redis import get_redis_connection
from django.db import transaction
from .models import OrderInfo,OrderGoods
from datetime import datetime


class CartSerializer(serializers.ModelSerializer):

    count = serializers.IntegerField(max_value=1)

    class Meta:
        model = SKU
        fields =['id','name','price','default_image_url','count']


class OrderSettlementSerializer(serializers.Serializer):

    freight = serializers.IntegerField(min_value=1)
    skus= CartSerializer(many=True)


class SaveOrderSerializer(serializers.Serializer):

    address = serializers.IntegerField(write_only=True)
    order_id = serializers.CharField(read_only=True)
    pay_method = serializers.IntegerField(write_only=True)

    def validate_pay_method(self,value):
        if value  not in [1,2]:
            raise serializers.ValidationError('支付方式错误')
        return value

    def validate_address(self,value):
        count = Address.objects.filter(pk = value).count()
        if count<=0:
            raise serializers.ValidationError('收货地址错误')

        return value

    def create(self, validated_data):
        """创建订单"""
        user_id =self.context['request'].user.id
        order_id = datetime.now().strftime("%Y%m%d%H%M%S")+'%09d'%user_id
        address= validated_data.get('address')
        pay_method = validated_data.get('pay_method')
        total_count=0
        total_amount=0
        # redis中获取订单信息

        redis_cli = get_redis_connection('cart')
        redis_cart = redis_cli.hgetall('cart_%d'% user_id)

        redis_select = redis_cli.smembers('cart_selected_%d'% user_id)
        select_dict = [ int(i) for i in redis_select]
        cart_list = {}
        for key, value in redis_cart.items():
            cart_list[int(key)] = int(value)
        # 开启事物

        with transaction.atomic():
            save_id = transaction.savepoint()
            # 创建订单对象
            order_info = OrderInfo.objects.create(
                order_id=order_id,
                user_id =user_id,
                address_id =address,
                total_count = total_count,
                total_amount = total_amount,
                pay_method = pay_method,
                freight=10,
            )
            skus = SKU.objects.filter(id__in=select_dict)
            for sku in skus:
                sku_count = cart_list.get(sku.id)
                if sku_count > sku.stock:
                    # 库存不足回滚事物
                    transaction.savepoint_rollback(save_id)
                    raise serializers.ValidationError('库存不足')
                # 商品列表中就减少库存和增加销量
                # sku.stock -= sku_count
                # sku.sales += sku_count
                # 开启乐观锁
                stock = sku.stock - sku_count
                re = SKU.objects.filter(id = sku.id,stock =sku.stock).update(stock = stock)

                if re == 0:
                    transaction.savepoint_rollback(save_id)
                    raise serializers.ValidationError('当前购买人数太多')

                OrderGoods.objects.create(
                    order_id = order_id,
                    sku_id = sku.id,
                    count = sku_count,
                    price = sku.price
                )

                total_count += sku_count
                total_amount += sku.price *sku_count


            order_info.total_count = total_count
            order_info.total_amount =total_amount
            order_info.save()
            transaction.savepoint_commit(save_id)

        redis_cli.srem('cart_selected_%d'%user_id,*select_dict)
        redis_cli.hdel('cart_%d' % user_id, *cart_list)

        return order_info
