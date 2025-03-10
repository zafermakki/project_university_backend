from django.db import transaction
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.db.models import Sum
from .serializers import CartCreateSerializer, CartSer,PurchaseSerializer,CartProductUpdateSerializer
from .models import CartProduct,Purchase


@api_view(['POST'])
def AddCart(request):
    print("Received Data:", request.data) 
    ser = CartCreateSerializer(data=request.data)
    if ser.is_valid():
        ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)
    
    # إذا كانت البيانات غير صالحة (مثل وجود المنتج بالفعل)
    return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def getByUserCart(request, id):
    data = CartProduct.objects.filter(cart__customer__pk=id)
    ser = CartSer(data, many=True)
    return Response(ser.data)

@api_view(['DELETE'])
def deleteCartItem(request, product_id):
    try:
        # Find the CartProduct entry based on the provided product_id
        cart_product = CartProduct.objects.get(id=product_id)
        cart_product.delete()
        return Response({"message": "Product removed from cart"}, status=status.HTTP_204_NO_CONTENT)
    except CartProduct.DoesNotExist:
        return Response({"error": "Product not found in cart"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def complete_purchase(request, customer_id):
    try:
        with transaction.atomic():
        # Get cart products for the customer
            cart_products = CartProduct.objects.select_for_update().filter(cart__customer__id=customer_id)

            if not cart_products.exists():
                return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if there is enough stock for each product
            for cart_product in cart_products:
                if cart_product.quantity > cart_product.product.quantity:
                    # Return the remaining quantity available for this product
                    remaining_quantity = cart_product.product.quantity
                    return Response({
                        "error": f"Not enough stock for {cart_product.product.name}. Available: {remaining_quantity}"
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Create a purchase record for each product in the cart
            for cart_product in cart_products:
                Purchase.objects.create(
                    customer=cart_product.cart.customer,
                    product=cart_product.product,
                    quantity=cart_product.quantity
                )
                # Reduce product stock
                cart_product.product.quantity -= cart_product.quantity
                cart_product.product.save()

            # Clear cart after successful purchase
            cart_products.delete()

            return Response({"message": "Purchase completed successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['PUT'])
def update_cart_quantity(request, product_id):
    try:
        # Retrieve the CartProduct entry
        cart_product = CartProduct.objects.get(id=product_id)
        
        # Deserialize the request data
        serializer = CartProductUpdateSerializer(cart_product, data=request.data)
        
        if serializer.is_valid():
            # Update the quantity
            updated_cart_product = serializer.save()
            return Response(CartSer(updated_cart_product).data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except CartProduct.DoesNotExist:
        return Response({"error": "Product not found in cart"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_purchases_by_customer(request, customer_id):
    try:
        # Retrieve all purchases made by the customer
        purchases = Purchase.objects.filter(customer__id=customer_id)

        if not purchases.exists():
            return Response({"message": "No purchases found for this customer"}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the purchase data
        serializer = PurchaseSerializer(purchases, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def top_purchased_products(request):
    top_products = (
        Purchase.objects.values('product__id','product__name', 'product__image_path')
        .annotate(total_quantity= Sum('quantity'))
        .order_by('-total_quantity')[:10]
    )
    
    return Response(top_products)