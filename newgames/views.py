from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import viewsets,permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from products.models import SubCategory
from .models import Newgames
from .serializers import NewgameModelSerializer,GameTypeSerializer

@api_view(['GET'])
def getNewgames(request):
    newgames = Newgames.objects.all()
    ser = NewgameModelSerializer(newgames, many= True)
    return Response(data = ser.data, status = status.HTTP_200_OK)

class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class NewGamesViewSet(viewsets.ModelViewSet):
    queryset = Newgames.objects.all()
    serializer_class = NewgameModelSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsSuperUser]
    
class GameTypeList(APIView):
    def get(self, request):
        game_types = SubCategory.objects.filter(parent_category__name='Games')
        serializer = GameTypeSerializer(game_types, many=True)
        return Response(serializer.data)
        