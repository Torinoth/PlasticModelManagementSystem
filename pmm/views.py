from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
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
        return Response({
            'username': request.user.username,
            'isAuthenticated': True,
            'isStaff': request.user.is_staff,
        })
    return Response({'isAuthenticated': False})


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '').strip()
    if not username or not password:
        return Response(
            {'detail': 'ユーザー名とパスワードは必須です。'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if len(password) < 8:
        return Response(
            {'detail': 'パスワードは8文字以上で入力してください。'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if User.objects.filter(username=username).exists():
        return Response(
            {'detail': 'このユーザー名は既に使用されています。'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    User.objects.create_user(username=username, password=password, is_active=False)
    return Response(
        {'detail': '登録申請を受け付けました。管理者の承認をお待ちください。'},
        status=status.HTTP_201_CREATED,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_view(request):
    if not request.user.is_staff:
        return Response(status=status.HTTP_403_FORBIDDEN)
    users = User.objects.all().order_by('-date_joined')
    data = [
        {
            'id': u.id,
            'username': u.username,
            'is_active': u.is_active,
            'is_staff': u.is_staff,
            'date_joined': u.date_joined,
            'last_login': u.last_login,
        }
        for u in users
    ]
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_user_view(request, user_id):
    if not request.user.is_staff:
        return Response(status=status.HTTP_403_FORBIDDEN)
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    return Response({'detail': f'{user.username} を承認しました。'})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def suspend_user_view(request, user_id):
    if not request.user.is_staff:
        return Response(status=status.HTTP_403_FORBIDDEN)
    if request.user.id == user_id:
        return Response(
            {'detail': '自分自身を停止することはできません。'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    return Response({'detail': f'{user.username} を停止しました。'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_view(request, user_id):
    if not request.user.is_staff:
        return Response(status=status.HTTP_403_FORBIDDEN)
    if request.user.id == user_id:
        return Response(
            {'detail': '自分自身を削除することはできません。'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class KitPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ReadAllowAnyMixin:
    def get_permissions(self):
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return [AllowAny()]
        return [IsAuthenticated()]


class MakerViewSet(ReadAllowAnyMixin, viewsets.ModelViewSet):
    queryset = Maker.objects.all()
    serializer_class = MakerSerializer


class BrandViewSet(ReadAllowAnyMixin, viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class ScaleViewSet(ReadAllowAnyMixin, viewsets.ModelViewSet):
    queryset = Scale.objects.all()
    serializer_class = ScaleSerializer


class TagViewSet(ReadAllowAnyMixin, viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class KitViewSet(ReadAllowAnyMixin, viewsets.ModelViewSet):
    serializer_class = KitSerializer
    pagination_class = KitPagination

    def get_queryset(self):
        queryset = Kit.objects.select_related('brand__maker', 'brand', 'scale').prefetch_related('tags')
        tags_param = self.request.query_params.get('tags')
        if tags_param:
            tag_ids = [int(t) for t in tags_param.split(',') if t.strip().isdigit()]
            if tag_ids:
                queryset = queryset.filter(tags__id__in=tag_ids).distinct()
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(creationstatus__status=status_param).distinct()
        return queryset

    @action(detail=False, methods=['get'])
    def summary(self, request):
        s = CreationStatus.Status
        inactive = [s.SOLD, s.PARTED_OUT]

        excluded_ids = (
            CreationStatus.objects
            .filter(status__in=inactive)
            .values_list('kit_id', flat=True)
            .distinct()
        )
        active = Kit.objects.exclude(pk__in=excluded_ids)

        top_tags = list(
            Tag.objects
            .annotate(kit_count=Count('kits', filter=~Q(kits__id__in=excluded_ids)))
            .filter(kit_count__gt=0)
            .order_by('-kit_count')
            .values('id', 'name', 'kit_count')[:5]
        )

        return Response({
            'total_kits': active.count(),
            'backlog': active.filter(creationstatus__status=s.BACKLOG).distinct().count(),
            'in_progress': active.filter(creationstatus__status=s.IN_PROGRESS).distinct().count(),
            'completed': active.filter(creationstatus__status=s.COMPLETED).distinct().count(),
            'tags_top': top_tags,
        })


class CreationStatusViewSet(ReadAllowAnyMixin, viewsets.ModelViewSet):
    queryset = CreationStatus.objects.all()
    serializer_class = CreationStatusSerializer
