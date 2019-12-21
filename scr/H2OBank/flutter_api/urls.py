from django.urls import path, include
# from account.api import RegisterAPI, UserAPI, FileUploadAPI, GetFilesAPI
from django.conf import settings
from django.conf.urls.static import static
from rest_auth.urls import LogoutView, LoginView

# /api/auth/*
urlpatterns = [
    path('', include('rest_auth.urls')),

    # path('login/', LoginView.as_view(), name="rest_login"),
    # path('logout/', LogoutView.as_view(), name="rest_logout"),
    # path('auth/register/', RegisterAPI.as_view()),
    # path('auth/user/',UserAPI.as_view()),
    
    # path('file/encrypt/', FileAPI.as_view())
]