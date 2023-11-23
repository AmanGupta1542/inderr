
from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name="dashboard"),
    path('login/', user_login, name="login"),
    path('logout/', user_logout, name="logout"),
    path('change_password/', change_password),
    path('trains/', trains, name="trains"),
    path('map-place-distance/', cal_distance, name="cal_distance"),
    path('uploads/', file_uploads, name="file_uploads"),
    path('get_lat_lon/', get_lat_lon, name="get_lat_lon"),
    path('get_lat_lon2/', get_lat_lon2, name="get_lat_lon2"),
    path('send_data_rsp/', send_data_rsp, name="send_data_rsp"),
    path('get_updated_info/', get_updated_info, name="get_updated_info"),
    path("train_details/<int:train_number>/", train_details, name="train_details"),
]