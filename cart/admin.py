from django.contrib import admin
from .models import Cart, CartProduct,Purchase

admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(Purchase)
