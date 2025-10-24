from rest_framework import status
from django.urls import reverse

health_check_url = reverse('health_check')
vibe_check_url = reverse('vibe_check')

def test_health_check(client):
    response = client.get(health_check_url)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'message': 'pong'}

def test_vibe_check_missing_topic(client):
    response = client.post(vibe_check_url, data={})
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"error": "Missing topic"}

def test_vibe_check_success(client, mocker):
    topic = "test topic"
    mock_summary = {
        "avg_sentiment": 0.001,
        "breakdown": {"positive": 1, "negative": 0},
        "posts_analyzed": 2,
        "relevant_comments": 5,
        "timestamp": "2024-01-01T00:00:00",
        "vibe": "chill",
    }

    mock_fetch = mocker.patch('api.views.fetch_reddit_posts', return_value=['post1', 'post2'])
    mock_analyze = mocker.patch('api.views.analyze_posts', return_value=['analyzed1', 'analyzed2'])
    mock_summarise = mocker.patch('api.views.summarise_vibes', return_value=mock_summary)

    response = client.post(vibe_check_url, data={'topic': topic})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == mock_summary

    mock_fetch.assert_called_once_with(topic)
    mock_analyze.assert_called_once_with(['post1', 'post2'])
    mock_summarise.assert_called_once_with(['analyzed1', 'analyzed2'], topic)
