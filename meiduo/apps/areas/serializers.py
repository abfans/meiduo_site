from rest_framework.serializers import ModelSerializer

from areas.models import Area


class AreasSerializer(ModelSerializer):
    """展示省区域"""
    class Meta:
        model = Area
        fields= ['id','name']


class SubsAreaSerializer(ModelSerializer):
    """查询详细地址"""
    subs = AreasSerializer(many=True, read_only=True)

    class Meta:
        model = Area
        fields =['id','name','subs']