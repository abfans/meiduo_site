from django.shortcuts import render
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from .serializers import *
from .models import Goods
from utils.pagination import StandardResultsSetPagination
from drf_haystack.viewsets import HaystackViewSet

# Create your views here.
class SPUViews(ListAPIView):

    serializer_class = SKUSerializers
    pagination_class = StandardResultsSetPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ('create_time', 'price', 'sales')

    def get_queryset(self):
        return SKU.objects.filter(category=self.kwargs['category_id'])


# class SKUSearchViewSet(HaystackViewSet):
#     """
#     SKU搜索
#     """
#     index_models = [SKU]
#     pagination_class = StandardResultsSetPagination
#
#     serializer_class = SKUIndexSerializer