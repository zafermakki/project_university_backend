from django.urls import path
from . import views
from uuid import UUID
from .views import PurchaseListView


urlpatterns = [
    path('add/', views.AddCart),
    path('table-purchases/', PurchaseListView.as_view(), name='purchases'),
    path('<uuid:id>/', view= views.getByUserCart),
    path('delete/<int:product_id>/', views.deleteCartItem),
    path('complete-purchase/<uuid:customer_id>/', views.complete_purchase),
    path('update/<int:product_id>/', views.update_cart_quantity),
    path('purchases/<uuid:customer_id>/', views.get_purchases_by_customer),
    path('top_products/', views.top_purchased_products),
]
