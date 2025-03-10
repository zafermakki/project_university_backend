from django.contrib import admin
from .models import User

# admin.site.register(PendingUser)

# فلتر مخصص لعرض الزبائن أو المدراء فقط
class UserFilter(admin.SimpleListFilter):
    title = 'User Type'  # عنوان الفلتر
    parameter_name = 'user_type'  # اسم المعامل في URL

    def lookups(self, request, model_admin):
        # القيم التي ستظهر في الفلتر
        return (
            ('client', 'Clients'),           # عرض العملاء
            ('admin', 'Admins'),             # عرض المدراء
            ('exclude_clients', 'Exclude Clients'),  # الجميع ما عدا العملاء
        )

    def queryset(self, request, queryset):
        # تنفيذ الفلتر بناءً على القيم المحددة
        value = self.value()
        if value == 'client':
            return queryset.filter(is_client=True)  # العملاء فقط
        elif value == 'admin':
            return queryset.filter(is_superuser=True)  # المدراء فقط
        elif value == 'exclude_clients':
            return queryset.exclude(is_client=True)  # الجميع ما عدا العملاء
        return queryset  # إذا لم يتم تحديد قيمة، عرض الجميع

# تسجيل المستخدم في واجهة الإدارة مع إضافة الفلتر
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_client', 'is_superuser', 'is_active')  # الأعمدة المعروضة
    list_filter = (UserFilter, 'is_active')  # إضافة الفلتر المخصص مع الفلاتر الأخرى
    search_fields = ('username', 'email')  # إمكانية البحث باستخدام الاسم أو البريد الإلكتروني
