from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import Maker, Brand, Scale, Tag, Kit, CreationStatus
from .serializers import (
    MakerSerializer, BrandSerializer, ScaleSerializer,
    TagSerializer, KitSerializer, CreationStatusSerializer,
)


@ensure_csrf_cookie
@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_view(request):
    return Response({'detail': 'ok'})


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username', '')
    password = request.data.get('password', '')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return Response({'username': user.username})
    return Response(
        {'detail': 'ユーザー名またはパスワードが正しくありません。'},
        status=status.HTTP_401_UNAUTHORIZED,
    )


@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({'detail': 'ログアウトしました。'})


@api_view(['GET'])
@permission_classes([AllowAny])
def me_view(request):
    if request.user.is_authenticated:
        return Response({'username': request.user.username, 'isAuthenticated': True})
    return Response({'isAuthenticated': False}, status=status.HTTP_401_UNAUTHORIZED)


class KitPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class MakerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Maker.objects.all()
    serializer_class = MakerSerializer


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class ScaleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Scale.objects.all()
    serializer_class = ScaleSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class KitViewSet(viewsets.ModelViewSet):
    serializer_class = KitSerializer
    pagination_class = KitPagination

    def get_queryset(self):
        queryset = Kit.objects.select_related('brand__maker', 'brand', 'scale').prefetch_related('tags')
        tags_param = self.request.query_params.get('tags')
        if tags_param:
            tag_ids = [int(t) for t in tags_param.split(',') if t.strip().isdigit()]
            if tag_ids:
                queryset = queryset.filter(tags__id__in=tag_ids).distinct()
        return queryset


class CreationStatusViewSet(viewsets.ModelViewSet):
    queryset = CreationStatus.objects.all()
    serializer_class = CreationStatusSerializer
