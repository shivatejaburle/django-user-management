from django.urls import path

from  accounts.views import LogInView, LogOutView

app_name = "accounts"

urlpatterns = [
    path('log-in/', LogInView.as_view(), name='log_in'),
    path('log-out/', LogOutView.as_view(), name='log_out'),
]
