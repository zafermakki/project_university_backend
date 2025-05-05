from rest_framework import serializers
from .models import Cart, CartProduct, Product, Purchase,DeliveryAssignment
from users.models import User

class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartProduct
        fields = '__all__'
        
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'

class PurchaseSerializer(serializers.ModelSerializer):
    image_path = serializers.CharField(source='product.image_path', read_only=True)
    class Meta:
        model = Purchase
        fields = '__all__'
        
class CartProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartProduct
        fields = ['id', 'quantity']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value


class CartProductsCreateSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField()

class CartCreateSerializer(serializers.Serializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    products = CartProductsCreateSerializer(write_only=True, many=True)

    def create(self, validated_data):
        try:
            print("Starting cart creation...")
            products_data = validated_data.pop('products')
            customer = validated_data['customer']
            
            # Get or create a cart for the customer
            cart, created = Cart.objects.get_or_create(customer=customer)
            print(f"Cart found or created for customer {customer.username}")

            # Check if the product is already in the cart (no quantity validation)
            for product_data in products_data:
                product = product_data['id']
                print(f"Checking product {product.name}")

                if CartProduct.objects.filter(cart=cart, product=product).exists():
                    raise serializers.ValidationError({
                        "product": f"{product.name} is already in the cart."
                    })

            # Add products to the cart after checking if they exist (no stock quantity check)
            for product_data in products_data:
                product = product_data['id']
                quantity = product_data['quantity']

                # Add product to the cart
                try:
                    CartProduct.objects.create(product=product, cart=cart, quantity=quantity)
                    print(f"Product {product.name} added to cart.")
                except Exception as e:
                    raise serializers.ValidationError({
                        "cart": f"Error adding product {product.name} to the cart. Error: {str(e)}"
                    })

            print("Cart creation completed successfully.")
            return cart

        except Exception as e:
            print(f"Error during cart creation: {str(e)}")
            raise serializers.ValidationError({"error": str(e)})


class CartSer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=250, source='product.name')
    category = serializers.CharField(
        max_length=250, 
        source='product.sub_category.parent_category.name'
    )
    sub_category = serializers.CharField(
        max_length=250, 
        source='product.sub_category.name'
    )
    price = serializers.DecimalField(max_digits=20, decimal_places=4, source='product.price')
    final_price = serializers.DecimalField(max_digits=20, decimal_places=4, source='product.final_price', read_only=True)
    image_path = serializers.CharField(max_length=250, source='product.image_path')
    quantity = serializers.IntegerField()

# admin pages 
class TablePurchaseSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField()
    product = serializers.StringRelatedField()
    delivered = serializers.SerializerMethodField()
    delivery_provider = serializers.SerializerMethodField()

    class Meta:
        model = Purchase
        fields = ['id', 'customer', 'product', 'quantity', 'purchase_date', 'delivered','delivery_provider']
        
    def get_delivered(self, obj):
        assignment = getattr(obj, 'delivery_assignment', None)
        return assignment.delivered if assignment else False

    def get_delivery_provider(self, obj):
        assignment = getattr(obj, 'delivery_assignment', None)
        if not assignment:
            return None

        if assignment.delivery_provider:
            return assignment.delivery_provider.email

        return assignment.provider_email
        
class DeliveryAssignmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAssignment
        fields = ['purchase', 'delivery_provider', 'provider_email','delivered']
        read_only_fields = ['provider_email']

    def validate(self, data):
    # حالة "تعديل"
        if self.instance:
        # إذا تم تغيير الـ purchase، تحقق من التكرار
            if 'purchase' in data and data['purchase'] != self.instance.purchase:
                if DeliveryAssignment.objects.filter(purchase=data['purchase']).exclude(id=self.instance.id).exists():
                    raise serializers.ValidationError("This purchase already has an assigned delivery provider.")
        else:
        # حالة "إنشاء"
            if DeliveryAssignment.objects.filter(purchase=data['purchase']).exists():
                raise serializers.ValidationError("This purchase already has an assigned delivery provider.")
        return data


class MyDeliveriesSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source='purchase.product.name')
    quantity = serializers.IntegerField(source='purchase.quantity')
    recipient = serializers.EmailField(source='purchase.customer.email')
    purchase_date = serializers.DateTimeField(source='purchase.purchase_date', format="%Y-%m-%dT%H:%M:%SZ")

    class Meta:
        model  = DeliveryAssignment
        fields = ['id', 'product', 'quantity', 'recipient', 'purchase_date', 'delivered']