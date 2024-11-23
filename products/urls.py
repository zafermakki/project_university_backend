from django.urls import path
from . import views

urlpatterns = [
    path('categories/', view= views.getCategories),
    path('subcategories/', view = views.getSubCategories),
     path('search/<int:subcategory_id>/', views.searchProducts, name='search_products'),
    path('subcategories/prodcuts/<int:subcategory_id>/', view= views.getProductsBySubCategoryId),
    path('subcategories/<int:id>/', view = views.getSubCategoriesByCatId),
    path('<int:id>/', view= views.getProductsByCatId),
    path('', view= views.getProducts),
    
]
