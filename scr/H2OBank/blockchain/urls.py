from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from blockchain import views
from blockchain.views import *

urlpatterns = [
    path('api/get_chain', views.get_chain, name="get_chain"),
    path('api/mine_block', views.mine_block, name="mine_block"),
    path('api/is_valid', views.is_valid, name="is_valid"),
    path('api/add_transaction', views.add_transaction, name="add_transaction"), 
    path('api/connect_node', views.connect_node, name="connect_node"), 
    path('api/replace_chain', views.replace_chain, name="replace_chain"),

    path('test', views.test.as_view(), name="test"),
]
