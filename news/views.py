from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import News
from .serializers import NewsSerializer

@api_view(['GET'])
def news(request):
    news = News.objects.all().order_by('-created_at')
    serializer = NewsSerializer(news, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)