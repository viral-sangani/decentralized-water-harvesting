from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/iot/', include('blockchain.urls')),
    path('account/', include('account.urls')),
    path('', include('website.urls')),
]
