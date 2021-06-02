from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    # # path(r'', views.test, name="test"),
    

    path(r'', views.Index, name="index"),
    path(r'authen/', views.ChangPw, name="ChangPw"),
    # path('test/', views.test),
    # path('deletecookie/', views.access_session),
    # path('deletesession/', views.delete_session),



]
