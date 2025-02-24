from django.urls import path
from . import views
from uuid import UUID


urlpatterns = [
    path('add/', views.AddCart),
    path('<uuid:id>/', view= views.getByUserCart),
    path('delete/<int:product_id>/', views.deleteCartItem),
    path('complete-purchase/<uuid:customer_id>/', views.complete_purchase),
    path('update/<int:product_id>/', views.update_cart_quantity),
    path('purchases/<uuid:customer_id>/', views.get_purchases_by_customer),
    path('top_products/', views.top_purchased_products),
]
