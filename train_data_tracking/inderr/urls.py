
from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name="dashboard"),
    path('login/', user_login, name="login"),
    path('logout/', user_logout, name="logout"),
    path('change_password/', change_password),
]