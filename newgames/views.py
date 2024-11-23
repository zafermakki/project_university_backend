from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from .models import Newgames
from .serializers import NewgameModelSerializer

@api_view(['GET'])
def getNewgames(request):
    newgames = Newgames.objects.all()
    ser = NewgameModelSerializer(newgames, many= True)
    return Response(data = ser.data, status = status.HTTP_200_OK)