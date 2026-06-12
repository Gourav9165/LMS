# transactions/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('issue/<int:book_id>/', views.issue_book, name='issue_book'),
    path('return/<int:record_id>/', views.return_book, name='return_book'),
    path('reserve/<int:book_id>/', views.reserve_book, name='reserve_book'),
    path('receipt/<int:record_id>/', views.generate_receipt, name='generate_receipt'),]