from alipay import AliPay
from django.shortcuts import render

# Create your views here.
from rest_framework.views import Response
from rest_framework.views import APIView
from . models import Payment
from goods.models import SKU
from django.conf import settings
from orders.models import OrderInfo


class PaymentView(APIView):
    def get(self,request,order_id):
        try:
            order = OrderInfo.objects.get(pk = order_id)
        except:
            return Response({'message': '订单信息有误'}, status=400)


        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=settings.ALIPAY_URL,
            app_private_key_path= settings.ALIPAY_PRIVATE_PATH,
            alipay_public_key_path=settings.ALIPAY_PUBLIC_PATH,
            sign_type=settings.SIGN_TYPE,
            debug=settings.ALIPAY_DEBUG

        )
        order_str = alipay.api_alipay_trade_page_pay(
            out_trade_no = order_id,
            total_amount=str(order.total_amount),
            subject="美多商城%s" % order_id,
            return_url="http://www.meiduo.site:8080/pay_success.html",
        )
        alipay_url =settings.ALIPAY_URL + order_str
        return Response({'alipay_url': alipay_url})


class PaymentStatusView(APIView):
    def put(self,request):

        parmar = request.query_params.dict()
        signature = parmar.pop('sign')
        order_id = parmar.get('out_trade_no')


        alipay =AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_path=settings.ALIPAY_PRIVATE_PATH,
            alipay_public_key_path=settings.ALIPAY_PUBLIC_PATH,
            sign_type=settings.SIGN_TYPE,
            debug=settings.ALIPAY_DEBUG
        )
        success = alipay.verify(parmar,signature)

        if success:
            try:
                order = OrderInfo.objects.get(pk=order_id)
            except:
                raise Exception("订单编号无效")
            else:
                order.status = 2
                order.save()
            Payment.objects.create(
                order_id = order_id,
                trade_id = parmar.get('trade_no')
            )
            return Response({'trade_id': parmar.get('trade_no')})