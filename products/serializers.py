from rest_framework import serializers
from .models import Product, Category,SubCategory

class CategoryModelSerializer(serializers.ModelSerializer):
    class Meta:
        model= Category
        fields= '__all__'
        
class ProductModelSerializer(serializers.ModelSerializer):
    class Meta:
        model= Product
        fields= '__all__'
        
class SubCategoryModelSerializer(serializers.ModelSerializer):
    class Meta:
        model= SubCategory
        fields= '__all__'