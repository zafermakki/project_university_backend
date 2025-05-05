from django.contrib import admin
from .models import CartProduct,Purchase,DeliveryAssignment

# admin.site.register(Cart)


admin.site.register(CartProduct)
admin.site.register(DeliveryAssignment)


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'quantity', 'purchase_date')
    search_fields = ('product__name', 'customer__username')
    readonly_fields = ('customer', 'product', 'quantity')
    
