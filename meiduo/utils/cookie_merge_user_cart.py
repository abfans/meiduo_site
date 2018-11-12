from utils import re_json
from django_redis import get_redis_connection


def cookie_merge_cart(request,user,response):
    # 获取cookie中的购物商品
    cookie_cart = request.COOKIES.get('cart')
    if cookie_cart is None:
        return response
    cookie_cart= re_json.loads(cookie_cart)
    # 连接redis数据从中获取购物车
    redis_cli = get_redis_connection('cart')
    # 获取redis中所有商品的健
    for cookie_id,value in cookie_cart.items():
        # 保存cookie中商品的数量
        cookie_count = value.get('count')
        cookie_selected = value.get('selected')

        # 如果redis中存在就增加,不存在就创建
        redis_cli.hset('cart_%d' % user.id,cookie_id,cookie_count)

        # 获取redis中所有被选中的商品
        redis_select_dict = redis_cli.smembers('cart_selected_%s' %user.id)

        if cookie_selected:
            if cookie_id not in redis_select_dict:
                redis_cli.sadd('cart_selected_%s' % user.id,cookie_id)

    response.delete_cookie('cart')

    return response

