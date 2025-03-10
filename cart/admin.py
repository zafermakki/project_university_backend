from django.contrib import admin
from .models import CartProduct,Purchase

# admin.site.register(Cart)


admin.site.register(CartProduct)


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'quantity', 'purchase_date')
    search_fields = ('product__name', 'customer__username')
    readonly_fields = ('customer', 'product', 'quantity')
    
