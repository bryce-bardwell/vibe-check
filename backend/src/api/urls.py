from django.urls import path
from .views import health_check

urlpatterns = [
    path('ping/', health_check),
]
