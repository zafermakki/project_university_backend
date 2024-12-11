from rest_framework import serializers
from .models import Newgames

class NewgameModelSerializer(serializers.ModelSerializer):
    game_type = serializers.CharField(source='game_type.name', read_only=True)
    
    class Meta:
        model = Newgames
        fields = '__all__'