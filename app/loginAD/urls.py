from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    # path(r'', views.test, name="test"),
    path(r'', views.Index, name="index"),
    path(r'changpass/', views.ChangPw, name="ChangPw"),




]
