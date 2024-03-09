from django.urls import path

from  accounts.views import (
    LogInView, LogOutView, SignUpView, ActivateView,
)

app_name = "accounts"

urlpatterns = [
    path('log-in/', LogInView.as_view(), name='log_in'),
    path('log-out/', LogOutView.as_view(), name='log_out'),

    path('sign-up/', SignUpView.as_view(), name='sign_up'),
    path('activate/<code>/', ActivateView.as_view(), name='activate'),
]
