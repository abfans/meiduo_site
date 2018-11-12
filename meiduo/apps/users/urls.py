from  rest_framework_jwt.views import obtain_jwt_token
from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from . import views


urlpatterns=[
    url(r"^users/$",views.UsersView.as_view()),
    url(r"^user/$",views.UserView.as_view()),
    url(r"^authorizations/$",views.LoginView.as_view()),
    url(r"^emails/$",views.EmailsView.as_view()),
    url(r"^emails/verification/$",views.EmailVerificationView.as_view()),
    url(r"^browse_histories/$",views.BrwserHistoryView.as_view())
]

router = DefaultRouter()
router.register("addresses",views.AddressViewsets,base_name='addresses')

urlpatterns += router.urls