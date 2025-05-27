from django.db import models
from products.models import Product
from users.models import User
from django.db.models.signals import pre_delete
from django.dispatch import receiver

class Cart(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart"
        
    def __str__(self) -> str:
        return self.customer.username

class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "cart_products"
        
    def __str__(self) -> str:
        return f'{self.cart.customer.username} - {self.product.name}'

# جدول الشراء الجديد
class Purchase(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    purchase_date = models.DateTimeField(auto_now_add=True)
    country = models.CharField(null=True,blank=True,max_length=100)
    city = models.CharField(null=True,blank=True,max_length=100)
    phone = models.CharField(null=True,blank=True,max_length=20)
    price_at_purchase = models.DecimalField(max_digits=20, decimal_places=4,null=True,blank=True)

    class Meta:
        db_table = "purchase"

    def __str__(self) -> str:
        return f'{self.customer.username} bought {self.product.name} (Quantity: {self.quantity})'

class DeliveryAssignment(models.Model):
    purchase = models.OneToOneField(Purchase, on_delete=models.CASCADE, related_name='delivery_assignment')
    delivery_provider = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'is_delivery_provider': True}
        )
    provider_email = models.EmailField(null=True, blank=True)
    delivered = models.BooleanField(default=False)
    
    class Meta:
        db_table = "delivery_assignment"

    @receiver(pre_delete, sender=User)
    def preserve_completed_deliveries(sender, instance, **kwargs):
        DeliveryAssignment.objects.filter(
            delivery_provider=instance,
            delivered=True
        ).update(delivery_provider=None)
    
    def save(self, *args, **kwargs):
        if self.delivery_provider:
            self.provider_email = self.delivery_provider.email
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Delivery for {self.purchase.customer.email} by {self.delivery_provider.email}"