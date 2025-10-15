from django.contrib import admin
from django.urls import path, include  # include is required

urlpatterns = [
    path('api/', include('api.urls')),
]
