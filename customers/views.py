from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes
from rest_framework import status

from .models import Customer
from .serializers import CustomerModelSerializer

@api_view(['GET'])
def getUser(request, username):
    try:
        # البحث عن المستخدم بناءً على اسم المستخدم
        client = Customer.objects.get(username=username)
        serializer = CustomerModelSerializer(client)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Customer.DoesNotExist:
        # إذا لم يتم العثور على المستخدم
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def checkUser(request):
    data = request.data
    client= Customer.objects.filter(username= data['username'], 
                                  password= data['password']).first()
    if client is not None:
        serializer = CustomerModelSerializer(client)
        return Response(serializer.data, status= status.HTTP_200_OK)
    return Response({}, status= status.HTTP_404_NOT_FOUND)  

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])  # دعم multipart/form-data
def addUser(request):
    data = request.data
    serializer = CustomerModelSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

