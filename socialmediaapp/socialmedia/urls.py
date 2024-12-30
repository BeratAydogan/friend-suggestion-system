from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index),
    path('index', views.index,name='index'),
    path('followers_count',views.followers_count,name='followers_count'),
    path('graph/', views.draw_graph, name='draw_graph'),


]
