from django.contrib import admin
from .models import Category, SubCategory, Product, ProductRating


# @admin.register(SearchQuery)
# class SearchQueryAdmin(admin.ModelAdmin):
#     pass

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(ProductRating)
class ProductRatingAdmin(admin.ModelAdmin):
    list_display = ('product','user','rating')
    fields = ('product','user','rating')
    readonly_fields = ('product','user','rating')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sub_category','price','discount_percentage','final_price' ,'average_rating', 'quantity')
    list_filter = ('sub_category',)
    search_fields = ('name', 'sub_category__name', 'description')
    fields = ('name', 'average_rating', 'sub_category','release_date','games_type', 'description',
              'price', 'discount_percentage','final_price','image_path', 'video_url', 'quantity')

    readonly_fields = ('average_rating','final_price')
