from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generatemarkup/', views.generatemarkup, name='generatemarkup'),
]