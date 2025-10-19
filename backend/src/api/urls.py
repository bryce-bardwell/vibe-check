from django.urls import path
from .views import health_check, vibe_check

urlpatterns = [
    path('ping', health_check, name='health_check'),
    path('vibe', vibe_check, name='vibe_check')
]
