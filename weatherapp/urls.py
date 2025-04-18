from django.contrib import admin
from django.urls import path,include
from . import views
urlpatterns = [
    path('',views.weather_view,name='weather_view'),
]
