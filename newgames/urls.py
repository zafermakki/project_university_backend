from django.urls import path
from . import views

urlpatterns = [
    path('newgames/', view= views.getNewgames)
]
