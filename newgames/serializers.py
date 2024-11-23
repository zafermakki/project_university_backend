from rest_framework import serializers
from .models import Newgames

class NewgameModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newgames
        fields = '__all__'