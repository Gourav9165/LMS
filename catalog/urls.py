# catalog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.book_list, name='book_list'),
    path('dashboard/', views.analytics_dashboard, name='analytics_dashboard'),
]