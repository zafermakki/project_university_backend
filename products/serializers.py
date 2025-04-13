from rest_framework import serializers
from .models import Product, Category,SubCategory,ProductRating

class CategoryModelSerializer(serializers.ModelSerializer):
    class Meta:
        model= Category
        fields= '__all__'
        
class SubCategoryModelSerializer(serializers.ModelSerializer):
    parent_category_name = serializers.CharField(source='parent_category.name', read_only=True)
    parent_category_id = serializers.IntegerField(source='parent_category.id', read_only=True)
    class Meta:
        model= SubCategory
        fields= '__all__'
        
class ProductModelSerializer(serializers.ModelSerializer):
    average_rating = serializers.ReadOnlyField()
    final_price = serializers.ReadOnlyField()
    sub_category_detail = SubCategoryModelSerializer(source='sub_category', read_only=True)
    sub_category = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all())
    class Meta:
        model= Product
        fields = [
            'id', 'name', 'sub_category','sub_category_detail','release_date','games_type','description', 
            'price', 'discount_percentage','image_path', 'video_url', 'quantity',
            'average_rating','final_price'  # Include the overall rating field
        ]
        
        
class ProductRatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    product = serializers.StringRelatedField()
    class Meta:
        model = ProductRating
        fields = ['id', 'product', 'user', 'rating', 'created_at']
        
        