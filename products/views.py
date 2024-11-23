from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from .models import Category, Product,SubCategory
from .serializers import CategoryModelSerializer, ProductModelSerializer,SubCategoryModelSerializer

@api_view(['GET'])
def getCategories(request):
    categories= Category.objects.all()
    ser = CategoryModelSerializer(categories, many= True)
    return Response(data= ser.data, status= status.HTTP_200_OK)

@api_view(['GET'])
def getSubCategories(request):
    categories= SubCategory.objects.all()
    ser = SubCategoryModelSerializer(categories, many= True)
    return Response(data= ser.data, status= status.HTTP_200_OK)

@api_view(['GET'])
def getSubCategoriesByCatId(request, id):
    subcategories = SubCategory.objects.filter(parent_category_id=id)
    if not subcategories.exists():
        return Response({"detail": "No subcategories found for this category."}, status=status.HTTP_404_NOT_FOUND)
    ser = SubCategoryModelSerializer(subcategories, many=True)
    return Response(ser.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def getProductsBySubCategoryId(request, subcategory_id):
    products = Product.objects.filter(sub_category_id=subcategory_id)
    if not products.exists():
        return Response({"detail": "No products found for this subcategory."}, status=status.HTTP_404_NOT_FOUND)
    ser = ProductModelSerializer(products, many=True)
    return Response(ser.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def getProductsByCatId(request, id):
    products = Product.objects.filter(sub_category__parent_category_id=id)
    if not products.exists():
        return Response({"detail": "No products found for this category."}, status=status.HTTP_404_NOT_FOUND)
    ser = ProductModelSerializer(products, many=True)
    return Response(ser.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def getProducts(request):
    products = Product.objects.all()
    ser= ProductModelSerializer(products, many= True)
    return Response(ser.data, status= status.HTTP_200_OK)

@api_view(['GET'])
def searchProducts(request, subcategory_id):
    # الحصول على النص المدخل من خلال معلمات الطلب
    query = request.query_params.get('q', '').strip()  # تأكد من إزالة المسافات البيضاء
    if not query:
        return Response({"detail": "Please provide a search query."}, status=status.HTTP_400_BAD_REQUEST)

    # البحث في المنتجات الخاصة بالقسم الفرعي فقط
    products = Product.objects.filter(name__icontains=query, sub_category_id=subcategory_id)

    if not products.exists():
        return Response({"detail": "No products found matching the query in this subcategory."}, status=status.HTTP_404_NOT_FOUND)

    # تحويل النتائج إلى JSON باستخدام السيريلزر
    ser = ProductModelSerializer(products, many=True)
    return Response(ser.data, status=status.HTTP_200_OK)

