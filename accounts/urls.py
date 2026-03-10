from django.urls import path
from django.contrib.auth import views as auth_views
from .views import SignupView, LoginView, accounts_options, LogoutView, ForgotView, VerifyOTPView

urlpatterns = [
    path('', accounts_options, name='accounts_options'),
    path('signup/', SignupView, name='signup'),
    path('login/', LoginView, name='login'),
    path('logout/', LogoutView, name='logout'),
    path('forgot-password/', ForgotView, name='forgot_password'),
    path('verify-otp/', VerifyOTPView, name='verify_otp'),
]
