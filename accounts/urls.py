from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterUserView, BlackListTokenView, PeopleListView
from django.contrib.auth.views import PasswordResetView


app_name = 'accounts'
urlpatterns = [
    path('register/', RegisterUserView.as_view(), name="register_user"),
    path('logout/', BlackListTokenView.as_view(), name='logout_blacklist'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),

    # url paths from simpleJWT package
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # People
    path('people/', PeopleListView.as_view(), name='people'),
]
