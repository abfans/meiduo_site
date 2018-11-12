from django.db import models

from utils.models import BaseModel


# Creae your models here.
class OauthUser(BaseModel):
    """用户名QQ模型"""
    openid =  models.CharField(max_length=128,db_index=True)
    user =models.ForeignKey("users.User")

    class Meta:
        db_table = 'tb_oauth_user'