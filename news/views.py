from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework import viewsets,permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import BasePermission
from .models import News
from .serializers import NewsSerializer

@api_view(['GET'])
def news(request):
    news = News.objects.all().order_by('-created_at')
    serializer = NewsSerializer(news, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# admin pages

class HasDynamicPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        # ربط نوع العملية بالسماحية المطلوبة
        action_permission_map = {
            'list': 'view',
            'retrieve': 'view',
            'create': 'add',
            'update': 'change',
            'partial_update': 'change',
            'destroy': 'delete',
        }

        # اسم الموديل
        model_name = view.queryset.model._meta.model_name
        app_label = view.queryset.model._meta.app_label

        # نوع العملية المطلوبة (action)
        action = getattr(view, 'action', None)
        required_action = action_permission_map.get(action)

        if not required_action:
            return False

        # السماحية المطلوبة مثل: products.view_category
        perm_code = f"{app_label}.{required_action}_{model_name}"

        return request.user.has_perm(perm_code)

class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [HasDynamicPermission]