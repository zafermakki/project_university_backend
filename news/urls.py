from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import news,NewsViewSet


router = DefaultRouter()
router.register(r'allnews', NewsViewSet)

urlpatterns = [
    path('news/', news, name='news'),     
    path('', include(router.urls)),
]