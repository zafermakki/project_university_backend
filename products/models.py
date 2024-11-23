from django.db import models

# النموذج الرئيسي للأقسام (مثل قسم الأجهزة وقسم الألعاب)
class Category(models.Model):
    name = models.CharField(max_length=250, unique=True)
    image_path = models.ImageField(upload_to='categories/')
    description = models.TextField(default="", blank=True)

    class Meta:
        db_table = 'categories'

    def __str__(self) -> str:
        return self.name

# النموذج الخاص بالأقسام الفرعية (مثل ألعاب رعب، ألعاب أكشن)
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
    name = models.CharField(max_length=250)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="products",default=1)
    description = models.TextField(default="", blank=True)
    price = models.DecimalField(max_digits=20, decimal_places=4)
    image_path = models.ImageField(upload_to='products/')
    video_url = models.URLField(max_length=200, blank=True, null=True)
    quantity = models.IntegerField(default=0)

    class Meta:
        db_table = 'products'

    def __str__(self) -> str:
        return f"{self.name} ({self.sub_category.name} - {self.sub_category.parent_category.name})"
