from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from .views import *

urlpatterns = [
    path('login/', login_view, name="login_view"),
    path('register/', register_view, name="register_view"),
]
