from django.db import models

# Create your models here.
from utils.models import BaseModel


class Area(models.Model):
    name =models.CharField(max_length=10,verbose_name="名称")
    parent = models.ForeignKey('self',null=True,blank=True,related_name='subs',on_delete=models.SET_NULL)

    class Meta:
        db_table="tb_areas"
        verbose_name= "地区"

    def __str__(self):
        return self.name