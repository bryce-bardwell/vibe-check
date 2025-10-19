from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .services.vibe_service import fetch_reddit_posts, analyze_posts, summarise_vibes

@api_view(['GET'])
def health_check(request):
    content = {'message': 'pong'}
    return Response(content, status=status.HTTP_200_OK)

@api_view(["POST"])
def vibe_check(request):
    topic = request.data.get("topic")

    if not topic:
        return Response({"error": "Missing topic"}, status=status.HTTP_400_BAD_REQUEST)

    posts = fetch_reddit_posts(topic)
    analyzed = analyze_posts(posts)
    summary = summarise_vibes(analyzed, topic)

    return Response(summary, status=status.HTTP_200_OK)
