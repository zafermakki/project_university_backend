from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.db.models import Sum

from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.db.models import Avg

from .models import Category, Product,SubCategory,SearchQuery, ProductRating
from .serializers import CategoryModelSerializer, ProductModelSerializer,SubCategoryModelSerializer,ProductRatingSerializer
from .utils import get_content_based_recommendations

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

    try:
        subcategory = SubCategory.objects.get(id=subcategory_id)
    except SubCategory.DoesNotExist:
        return Response({"detail": "القسم الفرعي غير موجود."}, status=status.HTTP_404_NOT_FOUND)
    
    # تحديد المستخدم الحالي إذا كان مسجلاً
    user = request.user if request.user.is_authenticated else None
    
    # حفظ أو تحديث عملية البحث (يتم التفرد حسب الاستعلام والقسم الفرعي والمستخدم)
    search_query, created = SearchQuery.objects.get_or_create(
        query_text=query,
        subcategory=subcategory,
        user=user
    )
    search_query.count += 1
    search_query.save()
    
    # تحويل النتائج إلى JSON باستخدام السيريلزر
    ser = ProductModelSerializer(products, many=True)
    return Response(ser.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def searchRecommendations(request):
    """
    Endpoint لعرض توصيات المنتجات بناءً على بيانات عمليات البحث المخزنة للمستخدم
    دون الحاجة لتمرير معرف القسم الفرعي. يتم اختيار القسم الفرعي الذي يمتلك أعلى مجموع 
    عمليات البحث الخاصة بالمستخدم (أو بيانات البحث العامة في حال كان المستخدم غير مسجل) 
    ومن ثم استخدام أعلى عبارة بحث ضمن هذا القسم لعرض المنتجات.
    """
    # للمستخدمين المسجلين
    if request.user.is_authenticated:
        user_search_queries = SearchQuery.objects.filter(user=request.user)
        if not user_search_queries.exists():
            return Response({"detail": "لا توجد بيانات عمليات بحث للمستخدم."}, status=status.HTTP_404_NOT_FOUND)
        
        # تجميع عمليات البحث بحسب القسم الفرعي وحساب المجموع
        subcategory_counts = user_search_queries.values('subcategory').annotate(total_count=Sum('count')).order_by('-total_count')
        top_subcategory_id = subcategory_counts[0]['subcategory']
        
        try:
            subcategory = SubCategory.objects.get(id=top_subcategory_id)
        except SubCategory.DoesNotExist:
            return Response({"detail": "القسم الفرعي غير موجود."}, status=status.HTTP_404_NOT_FOUND)
        
        # اختيار أعلى عبارة بحث لهذا القسم للمستخدم
        search_queries = user_search_queries.filter(subcategory=subcategory).order_by('-count')
        top_query = search_queries.first().query_text
    else:
        # للمستخدمين غير المسجلين: استخدام بيانات البحث العامة
        global_search_queries = SearchQuery.objects.all()
        if not global_search_queries.exists():
            return Response({"detail": "لا توجد بيانات عمليات بحث."}, status=status.HTTP_404_NOT_FOUND)
        
        subcategory_counts = global_search_queries.values('subcategory').annotate(total_count=Sum('count')).order_by('-total_count')
        top_subcategory_id = subcategory_counts[0]['subcategory']
        
        try:
            subcategory = SubCategory.objects.get(id=top_subcategory_id)
        except SubCategory.DoesNotExist:
            return Response({"detail": "القسم الفرعي غير موجود."}, status=status.HTTP_404_NOT_FOUND)
        
        search_queries = global_search_queries.filter(subcategory=subcategory).order_by('-count')
        top_query = search_queries.first().query_text

    # استخدام أعلى عبارة بحث كمدخل لخوارزمية التوصية
    recommended_products = get_content_based_recommendations(top_query, subcategory.id, Product, top_n=5)
    if not recommended_products:
        return Response({"detail": "لا توجد منتجات موصى بها."}, status=status.HTTP_404_NOT_FOUND)
    
    serialized_recommendations = ProductModelSerializer(recommended_products, many=True)
    return Response(serialized_recommendations.data, status=status.HTTP_200_OK)
   
@api_view(['POST'])
def rate_product(request, product_id):
    # التأكد من أن المستخدم مسجل الدخول
    if not request.user.is_authenticated:
        return Response({"detail": "you should login first."}, status=status.HTTP_401_UNAUTHORIZED)
    
    product = get_object_or_404(Product, id=product_id)
    
    # الحصول على قيمة التقييم من البيانات المرسلة
    rating_value = request.data.get("rating")
    if rating_value is None:
        return Response({"detail": "the evaluation value must be provided."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        rating_value = Decimal(rating_value)
    except Exception:
        return Response({"detail": "the evaluation value is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
    
    # التأكد من أن قيمة التقييم ضمن القيم المسموحة (من 1.0 إلى 5.0 بخطوة 0.5)
    valid_ratings = [Decimal(i)/Decimal('2') for i in range(1, 11)]  # [0.5, 1.0, ..., 5.0] 
    if rating_value not in valid_ratings:
        return Response(
            {"detail": "يجب أن تكون قيمة التقييم من 1.0 إلى 5.0 بخطوة 0.5."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # التحقق مما إذا كان المستخدم قد قيّم المنتج مسبقًا وتحديثه، أو إنشاء تقييم جديد
    product_rating, created = ProductRating.objects.get_or_create(
        product=product, 
        user=request.user, 
        defaults={'rating': rating_value}
    )
    if not created:
        product_rating.rating = rating_value
        product_rating.save()
    
    # حساب المتوسط الجديد للتقييمات الخاصة بالمنتج
    avg = product.ratings.aggregate(average=Avg('rating'))['average']
    avg = round(avg, 2) if avg else 0
    
    return Response(
        {"detail": "successfully.", "average_rating": avg},
        status=status.HTTP_200_OK
    )
    
@api_view(['GET'])
def get_user_rating(request, product_id):
    if not request.user.is_authenticated:
        return Response({"details":"please login first"}, status=status.HTTP_401_UNAUTHORIZED)
    
    product = get_object_or_404(Product, id=product_id)
    
    try:
        product_rating = ProductRating.objects.get(product=product, user=request.user)
        serializer = ProductRatingSerializer(product_rating)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ProductRating.DoesNotExist:
        return Response({"details": "you have not yet evaluated this product"}, status=status.HTTP_404_NOT_FOUND)