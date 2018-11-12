from goods.models import GoodsChannel
from collections import OrderedDict


def category_list():
    """生成静态页面"""
    categories = OrderedDict()  # 生成有序字典
    # 对频道表排序查询
    channels = GoodsChannel.objects.order_by('group_id','sequence')
    for channel in channels:
        if channel.group_id not in categories:
            categories[channel.group_id] = {'channels': [],'sub_cats':[]}

        categories[channel.group_id]['channels'].append({
            'id': channel.id,
            'name': channel.category.name,
            'url': channel.url,
        })

        sub_cats= channel.category.goodscategory_set.all()
        for sub_cat in sub_cats:
            sub_cat.sub_cats =sub_cat.goodscategory_set.all()
            categories[channel.group_id]['sub_cats'].append(sub_cat)

    return categories