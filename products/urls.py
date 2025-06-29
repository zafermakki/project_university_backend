from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views
from .views import CategoryViewSet, SubCategoryViewSet,ProductViewSet,GameTypeChoicesView,ProductRatingListView,ProductSearchView

router = DefaultRouter()
router.register(r'allcategories', CategoryViewSet)
router.register(r'allsubcategories', SubCategoryViewSet)
router.register(r'allproducts', ProductViewSet)

urlpatterns = [
    path('categories/', view= views.getCategories),
    path('subcategories/', view = views.getSubCategories),
    path('offline_games/', view = views.offline_games),
    path('online_games/', view = views.online_games),
    path('discounted/', view = views.get_discounted_products),
    path('all/search/', ProductSearchView.as_view(), name='product-search'),
    path('rating/', ProductRatingListView.as_view(), name='product-ratings'),
    path('games-types/', GameTypeChoicesView.as_view(), name='games-types'),
    path('search/<int:subcategory_id>/', views.searchProducts, name='search_products'),
    path('rate-product/<int:product_id>/', views.rate_product, name='rate_product'),
    path('subcategories/prodcuts/<int:subcategory_id>/', view= views.getProductsBySubCategoryId),
    path('subcategories/<int:id>/', view = views.getSubCategoriesByCatId),
    path('search_recommendations/', views.searchRecommendations, name='searchRecommendations'),
    path('top-rated/', views.top_rated_products, name='top_rated_products'),
    path('medium-rated/', views.medium_rated_products, name='medium_rated_products'),
    path('low-rated/', views.low_rated_products, name='low_rated_products'),
    path('my-rating/<int:product_id>/', views.get_user_rating, name='get_user_rating'),
    path('<int:id>/', view= views.getProductsByCatId),
    path('', view= views.getProducts),
    
    path('', include(router.urls)),
]
