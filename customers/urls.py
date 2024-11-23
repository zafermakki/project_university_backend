from django.urls import path
from . import views

urlpatterns = [
    path('check-user/', view= views.checkUser),
    path('add-user/', view= views.addUser),
    path('get-user/<username>/', view= views.getUser)
]