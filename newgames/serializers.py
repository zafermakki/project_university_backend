from rest_framework import serializers
from .models import Newgames
from products.models import SubCategory

class NewgameModelSerializer(serializers.ModelSerializer):
    game_type_name = serializers.CharField(source='game_type.name', read_only=True)
    
    class Meta:
        model = Newgames
        fields = '__all__'
        
class GameTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'name']
        
