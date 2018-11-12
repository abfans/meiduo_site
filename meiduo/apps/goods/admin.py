# from django.contrib import admin
# from . import models
# from celery_tasks.html.tasks import generate_static_sku_detail_html
#
#
# class GoodsAdmin(admin.ModelAdmin):
#     list_display = ['id','name']
#
#     def save_model(self, request, obj, form, change):
#         super().save_model(request,obj,form,change)
#         generate_static_sku_detail_html.delay(obj.id)
#
#     def delete_model(self, request, obj):
#         pass
#
#
# admin.site.register(models.GoodsCategory)
# admin.site.register(models.GoodsChannel)
# admin.site.register(models.Goods)
# admin.site.register(models.Brand)
# admin.site.register(models.GoodsSpecification)
# admin.site.register(models.SpecificationOption)
# admin.site.register(models.SKU,GoodsAdmin)
# admin.site.register(models.SKUSpecification)
# admin.site.register(models.SKUImage)