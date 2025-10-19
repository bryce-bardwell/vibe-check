import pytest
from rest_framework import status
from django.urls import reverse

@pytest.mark.django_db
def test_health_check(client):
    url = reverse('health_check')
    response = client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'message': 'pong'}
