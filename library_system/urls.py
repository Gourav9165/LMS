from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('catalog.urls')),
    path('users/', include('users.urls')),
    
    # Add this missing line to connect your transactions app
    path('transactions/', include('transactions.urls')),
]