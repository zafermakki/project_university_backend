from django.urls import path
from . import views

urlpatterns = [
    path('categories/', view= views.getCategories),
    path('subcategories/', view = views.getSubCategories),
    path('search/<int:subcategory_id>/', views.searchProducts, name='search_products'),
    path('rate-product/<int:product_id>/', views.rate_product, name='rate_product'),
    path('subcategories/prodcuts/<int:subcategory_id>/', view= views.getProductsBySubCategoryId),
    path('subcategories/<int:id>/', view = views.getSubCategoriesByCatId),
    path('search_recommendations/', views.searchRecommendations, name='searchRecommendations'),
    path('my-rating/<int:product_id>/', views.get_user_rating, name='get_user_rating'),
    path('<int:id>/', view= views.getProductsByCatId),
    path('', view= views.getProducts),
    
]
