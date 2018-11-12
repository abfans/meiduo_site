from django.conf.urls import url
from . import views


urlpatterns=[
    url("^qq/authorization/",views.QOauth.as_view()),
    url("^qq/user/$",views.QoauthUserView.as_view())
]