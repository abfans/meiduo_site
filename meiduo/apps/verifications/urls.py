from rest_framework.urls import url
from . import views

urlpatterns=[
    url(r"^sms_code/(?P<mobile>1[3-9]\d{9})/",views.SMSCodeView.as_view()),
    url(r"^mobiles/(?P<mobile>1[3-9]\d{9})/count/$",views.MobilesView.as_view()),
    url(r"^usernames/(?P<username>\w{5,20})/count/$",views.UsernamesView.as_view()),
]