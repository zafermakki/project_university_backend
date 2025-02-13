from django.db import models
from products.models import Product
from users.models import User

class Cart(models.Model):
    customer = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart"
        
    def __str__(self) -> str:
        return self.customer.username

class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "cart_products"
        
    def __str__(self) -> str:
        return f'{self.cart.customer.username} - {self.product.name}'

# جدول الشراء الجديد
class Purchase(models.Model):
    customer = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    quantity = models.PositiveIntegerField()
    purchase_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "purchase"

    def __str__(self) -> str:
        return f'{self.customer.username} bought {self.product.name} (Quantity: {self.quantity})'
