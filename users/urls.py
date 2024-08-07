
from django.urls import path, include

from users.views import LoginView, RequestApproverejectView, RequestSendinView, UserConnectViewset, UserViewset,ListUsers
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r"user", UserViewset, basename="user")
router.register(r"user-connect", UserConnectViewset, basename="user-connect")

urlpatterns = [
    path('user-list/', ListUsers.as_view(), name = "user-list"),
    path("login/", LoginView.as_view(), name="token_obtain_pair"),
    path("request/", RequestSendinView.as_view(), name ="request-send"),
    path('ch/<int:pk>/', RequestApproverejectView.as_view(), name='request_update'),

    path("", include(router.urls)),
]
