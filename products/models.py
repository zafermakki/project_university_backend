from django.db import models
from django.conf import settings
from django.db.models import Avg
from decimal import Decimal
# النموذج الرئيسي للأقسام (مثل قسم الأجهزة وقسم الألعاب)
class Category(models.Model):
    name = models.CharField(max_length=250, unique=True)
    image_path = models.ImageField(upload_to='categories/')
    description = models.TextField(default="", blank=True)

    class Meta:
        db_table = 'categories'

    def __str__(self) -> str:
        return self.name

# النموذج الخاص بالأقسام الفرعية (مثل ألعاب رعب، ألعاب أكشن و اجهزة بلاي ستيشن و نظارات الواقع الافتراضي )
class SubCategory(models.Model):
    name = models.CharField(max_length=250, unique=True)
    parent_category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    image_path = models.ImageField(upload_to='subcategories/', blank=True, null=True)

    class Meta:
        db_table = 'sub_categories'

    def __str__(self) -> str:
        return f"{self.name} ({self.parent_category.name})"

# النموذج الخاص بالمنتجات
class Product(models.Model):
    GAME_TYPE_CHOICES = [
        ('offline', 'Offline'),
        ('online', 'Online'),
    ]
    name = models.CharField(max_length=250)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="products",default=1)
    release_date = models.DateField(null=True, blank=True)
    games_type = models.CharField(max_length=255,choices=GAME_TYPE_CHOICES,null=True,blank=True)
    description = models.TextField(default="", blank=True)
    price = models.DecimalField(max_digits=20, decimal_places=4)
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="the percentage of discount on the product"
    )
    image_path = models.ImageField(upload_to='products/')
    video_url = models.URLField(max_length=200, blank=True, null=True)
    quantity = models.IntegerField(default=0)

    class Meta:
        db_table = 'products'

    def __str__(self) -> str:
        return f"{self.name} ({self.sub_category.name} - {self.sub_category.parent_category.name})"

    @property
    def average_rating(self):
        """يحساب المتوسط لجميع تقييمات اللعبة"""
        avg = self.ratings.aggregate(average=Avg('rating'))['average']
        return round(avg, 2) if avg else 0
    
    @property
    def final_price(self):
        """the final price"""
        discount_value = (self.discount_percentage / 100) * self.price
        return self.price - discount_value
    
class ProductRating(models.Model):
    RATING_CHOICES = [
        (Decimal(i/2).quantize(Decimal('0.0')), f"{i/2} نجمة")
        for i in range(2, 11)  # 2/2=1.0, 3/2=1.5, ... , 10/2=5.0
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        choices=RATING_CHOICES,
        help_text="choose the rating of the game"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_ratings'
        unique_together = ('product', 'user')
        
    def __str__(self) -> str:
        return f"{self.user.username} - {self.product.name}: {self.rating}"


class SearchQuery(models.Model):
    query_text = models.CharField(max_length=255)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="search_queries")
    # ربط البحث بالمستخدم؛ في حال كان المستخدم غير مسجل يمكن تركه فارغاً
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="search_queries", null=True, blank=True)
    count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # يتم التفرد حسب الاستعلام والقسم الفرعي والمستخدم حتى لا يتكرر السجل لنفس المستخدم
        unique_together = ('query_text', 'subcategory', 'user')
        db_table = 'search_queries'

    def __str__(self):
        user_str = self.user.email if self.user else "Anonymous"
        return f"{self.query_text} in {self.subcategory.name} ({self.count} times) by {user_str}"