from django.urls import path
from . import views
from uuid import UUID
from .views import PurchaseListView,AssignDeliveryProviderView,MyDeliveriesListView,MarkDeliveredView,UpdateDeliveryProviderView

urlpatterns = [
    path('add/', views.AddCart),
    path('table-purchases/', PurchaseListView.as_view(), name='purchases'),
    path('assign-delivery/', AssignDeliveryProviderView.as_view(), name='assign-delivery'),
    path('my-deliveries/', MyDeliveriesListView.as_view(), name='my-deliveries'),
    path('delivery-assignment/<int:pk>/update/', UpdateDeliveryProviderView.as_view(), name='update-delivery-provider'),
    path('delivery/<int:pk>/delivered/', MarkDeliveredView.as_view(), name='mark-delivered'),
    path('<uuid:id>/', view= views.getByUserCart),
    path('delete/<int:product_id>/', views.deleteCartItem),
    path('complete-purchase/<uuid:customer_id>/', views.complete_purchase),
    path('update/<int:product_id>/', views.update_cart_quantity),
    path('purchases/<uuid:customer_id>/', views.get_purchases_by_customer),
    path('top_products/', views.top_purchased_products),
]
