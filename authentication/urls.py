from django.urls import path
from authentication import views

urlpatterns = [
    path('signup/',views.signup),
    path('login/',views.login_user),
    path('logout/',views.logout_user),
    path('activate/<str:uidb64>/<str:token>/',views.activate, name='activate'),
    path('forgot-password/',views.forgotpassword, name='forgotpassword'),
    path('verify_code/<str:email>/',views.verify_code, name='verify_code'),
    path('reset-password/<str:email>/',views.reset_password, name='reset_password'),
]