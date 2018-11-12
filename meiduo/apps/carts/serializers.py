from rest_framework import serializers

from goods.models import SKU
from django_redis import get_redis_connection


class CartsSerializer(serializers.Serializer):
    """购物车序列化"""
    sku_id  = serializers.IntegerField(min_value=1)
    count = serializers.IntegerField(min_value=1)
    selected = serializers.BooleanField(default=True)

    def validated_sku_id(self,value):
        try:
            SKU.objects.get(pk = value)
        except SKU.DoesNotExist:
            raise  serializers.ValidationError("商品不存在")
        return value

    def validated_count(self,value):
        if value <=0:
            raise serializers.ValidationError("不能加入购物车")

        return value

class CartListSerializer(serializers.ModelSerializer):

    count = serializers.IntegerField()
    selected = serializers.BooleanField()

    class Meta:
        model = SKU
        fields= ['id', 'count', 'name', 'default_image_url', 'price', 'selected']

class CartDeleteSerializer(serializers.Serializer):

    sku_id = serializers.IntegerField(min_value=1)

    def validate_sku_id(self, attr):
        try:
            sku = SKU.objects.get(pk = attr)
        except sku.DoesNotExist:
            raise serializers.ValidationError('商品不存在')

        return attr

class CartAllSerializer(serializers.Serializer):

    selected =serializers.BooleanField()
