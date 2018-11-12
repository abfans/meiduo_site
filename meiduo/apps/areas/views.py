from rest_framework.viewsets import ReadOnlyModelViewSet
from .serializers import *
# Create your views here.
from django.core.cache import cache
from rest_framework_extensions.cache.mixins import CacheResponseMixin


class AreasView(CacheResponseMixin,ReadOnlyModelViewSet):
    """展示地区"""
    def get_serializer_class(self):
        if self.action == "list":
            return AreasSerializer
        else:
            return SubsAreaSerializer

    def get_queryset(self):
        if self.action == "list":
            return Area.objects.filter(parent__isnull=True)
        else:
            return Area.objects.all()
