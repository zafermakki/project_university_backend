from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import NewGamesViewSet,GameTypeList
from . import views

router = DefaultRouter()
router.register(r'allnewgames', NewGamesViewSet)

urlpatterns = [
    path('newgames/', view= views.getNewgames),
    path('gametypes/', GameTypeList.as_view(), name='games-types'),
    path('', include(router.urls)),
]
