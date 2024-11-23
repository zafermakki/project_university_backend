from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.AddCart),
    path('<int:id>/', view= views.getByUserCart),
    path('delete/<int:product_id>/', views.deleteCartItem),
    path('complete-purchase/<int:customer_id>/', views.complete_purchase),
    path('update/<int:product_id>/', views.update_cart_quantity),
    path('purchases/<int:customer_id>/', views.get_purchases_by_customer),
]
