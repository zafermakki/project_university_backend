from rest_framework import serializers
from .models import Product, Category,SubCategory,ProductRating

class CategoryModelSerializer(serializers.ModelSerializer):
    class Meta:
        model= Category
        fields= '__all__'
        
class ProductModelSerializer(serializers.ModelSerializer):
    average_rating = serializers.ReadOnlyField()
    final_price = serializers.ReadOnlyField()
    class Meta:
        model= Product
        fields = [
            'id', 'name', 'sub_category','release_date','games_type','description', 
            'price', 'discount_percentage','image_path', 'video_url', 'quantity',
            'average_rating','final_price'  # Include the overall rating field
        ]
        
class SubCategoryModelSerializer(serializers.ModelSerializer):
    class Meta:
        model= SubCategory
        fields= '__all__'
        
class ProductRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRating
        fields = ['rating']