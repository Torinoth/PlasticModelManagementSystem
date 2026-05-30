from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.db.models import (
    Count, Q, Sum, F, Value, BooleanField,
    OuterRef, Subquery,
    Case, When, DurationField, ExpressionWrapper,
)
from django.db.models.functions import Now
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import Maker, Brand, Scale, Tag, Kit, CreationStatus, FavoriteMaker, FavoriteBrand, EmailVerificationToken
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
            'id': request.user.id,
            'username': request.user.username,
            'isAuthenticated': True,
            'isStaff': request.user.is_staff,
        })
    return Response({'isAuthenticated': False})


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    username = request.data.get('username', '').strip()
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '').strip()
    if not username or not email or not password:
        return Response(
            {'detail': 'ユーザー名・メールアドレス・パスワードは必須です。'},
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
    if User.objects.filter(email=email).exists():
        return Response(
            {'detail': 'このメールアドレスは既に登録されています。'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user = User.objects.create_user(username=username, email=email, password=password, is_active=False)
    token_obj = EmailVerificationToken.objects.create(user=user)
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token_obj.token}"
    try:
        send_mail(
            subject='【すこん部員のなにがし】メールアドレスの確認',
            message=(
                f'{username} さん、ご登録ありがとうございます。\n\n'
                f'以下のURLをクリックしてメールアドレスを認証してください。\n\n'
                f'{verify_url}\n\n'
                f'このメールに心当たりがない場合は無視してください。'
            ),
            from_email=settings.EMAIL_FROM,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception:
        user.delete()
        return Response(
            {'detail': '認証メールの送信に失敗しました。しばらく時間をおいて再度お試しください。'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return Response(
        {'detail': '認証メールを送信しました。メールをご確認ください。'},
        status=status.HTTP_201_CREATED,
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email_view(request):
    token_str = request.query_params.get('token', '').strip()
    if not token_str:
        return Response(
            {'detail': 'トークンが指定されていません。'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        token_obj = EmailVerificationToken.objects.select_related('user').get(
            token=token_str, is_used=False
        )
    except (EmailVerificationToken.DoesNotExist, ValueError):
        return Response(
            {'detail': '認証リンクが無効または期限切れです。'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user = token_obj.user
    user.is_active = True
    user.save()
    token_obj.is_used = True
    token_obj.save()
    return Response({'detail': 'メールアドレスの認証が完了しました。ログインしてください。'})


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
        if getattr(self, 'action', None) == 'favorite':
            return [IsAuthenticated()]
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAdminUser()]
        return [IsAuthenticated()]


class MakerViewSet(ReadAllowAnyMixin, viewsets.ModelViewSet):
    queryset = Maker.objects.all()
    serializer_class = MakerSerializer
    pagination_class = None

    def get_queryset(self):
        qs = Maker.objects.all()
        if self.request.user.is_authenticated:
            fav_ids = FavoriteMaker.objects.filter(
                user=self.request.user
            ).values_list('maker_id', flat=True)
            qs = qs.annotate(
                _is_fav=Case(
                    When(id__in=fav_ids, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            ).order_by('-_is_fav', 'name')
        else:
            qs = qs.order_by('name')
        return qs

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        maker = self.get_object()
        if request.method == 'POST':
            FavoriteMaker.objects.get_or_create(user=request.user, maker=maker)
            return Response({'is_favorite': True})
        FavoriteMaker.objects.filter(user=request.user, maker=maker).delete()
        return Response({'is_favorite': False})


class BrandViewSet(ReadAllowAnyMixin, viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    pagination_class = None

    def get_queryset(self):
        qs = Brand.objects.select_related('maker').all()
        if self.request.user.is_authenticated:
            fav_ids = FavoriteBrand.objects.filter(
                user=self.request.user
            ).values_list('brand_id', flat=True)
            qs = qs.annotate(
                _is_fav=Case(
                    When(id__in=fav_ids, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            ).order_by('-_is_fav', 'name')
        else:
            qs = qs.order_by('name')
        return qs

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        brand = self.get_object()
        if request.method == 'POST':
            FavoriteBrand.objects.get_or_create(user=request.user, brand=brand)
            return Response({'is_favorite': True})
        FavoriteBrand.objects.filter(user=request.user, brand=brand).delete()
        return Response({'is_favorite': False})


class ScaleViewSet(ReadAllowAnyMixin, viewsets.ModelViewSet):
    queryset = Scale.objects.all()
    serializer_class = ScaleSerializer
    pagination_class = None


class TagViewSet(ReadAllowAnyMixin, viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    pagination_class = None
    serializer_class = TagSerializer


class KitViewSet(ReadAllowAnyMixin, viewsets.ModelViewSet):
    serializer_class = KitSerializer
    pagination_class = KitPagination

    def get_queryset(self):
        queryset = Kit.objects.select_related('brand__maker', 'brand', 'scale', 'owner').prefetch_related('tags', 'creationstatus_set')

        if self.request.user.is_authenticated:
            queryset = queryset.filter(owner=self.request.user)
        else:
            return queryset.none()

        return _apply_kit_filters(queryset, self.request.query_params)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_object(self):
        obj = super().get_object()
        if self.request.method not in ('GET', 'HEAD', 'OPTIONS'):
            if obj.owner != self.request.user:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied('このキットを操作する権限がありません。')
        return obj

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
        if not request.user.is_authenticated:
            return Response({
                'total_kits': 0, 'backlog': 0, 'in_progress': 0, 'completed': 0,
                'total_price': 0, 'backlog_price': 0, 'in_progress_price': 0, 'completed_price': 0,
                'tags_top': [],
            })

        active = Kit.objects.exclude(pk__in=excluded_ids).filter(owner=request.user)

        top_tags = list(
            Tag.objects
            .annotate(kit_count=Count(
                'kits',
                filter=Q(kits__owner=request.user) & ~Q(kits__id__in=excluded_ids),
            ))
            .filter(kit_count__gt=0)
            .order_by('-kit_count')
            .values('id', 'name', 'kit_count')[:5]
        )

        backlog_qs     = active.filter(creationstatus__status=s.BACKLOG).distinct()
        in_progress_qs = active.filter(creationstatus__status=s.IN_PROGRESS).distinct()
        completed_qs   = active.filter(creationstatus__status=s.COMPLETED).distinct()

        def price_sum(qs):
            return int(qs.aggregate(total=Sum('price'))['total'] or 0)

        return Response({
            'total_kits':       active.count(),
            'backlog':          backlog_qs.count(),
            'in_progress':      in_progress_qs.count(),
            'completed':        completed_qs.count(),
            'total_price':      price_sum(active),
            'backlog_price':    price_sum(backlog_qs),
            'in_progress_price': price_sum(in_progress_qs),
            'completed_price':  price_sum(completed_qs),
            'tags_top':         top_tags,
        })


class CreationStatusViewSet(ReadAllowAnyMixin, viewsets.ModelViewSet):
    queryset = CreationStatus.objects.all()
    serializer_class = CreationStatusSerializer


def _apply_kit_filters(queryset, query_params):
    """タグ・ステータス・放置日数ソートを queryset に適用して返す。"""
    tags_param = query_params.get('tags')
    if tags_param:
        tag_ids = [int(t) for t in tags_param.split(',') if t.strip().isdigit()]
        if tag_ids:
            queryset = queryset.filter(tags__id__in=tag_ids).distinct()

    status_param = query_params.get('status')
    if status_param:
        queryset = queryset.filter(creationstatus__status=status_param).distinct()

    ordering_param = query_params.get('ordering')
    if ordering_param in ('days_since_updated', '-days_since_updated'):
        inactive = [
            CreationStatus.Status.COMPLETED,
            CreationStatus.Status.SOLD,
            CreationStatus.Status.PARTED_OUT,
        ]
        latest_cs = CreationStatus.objects.filter(kit=OuterRef('pk')).order_by('-id')
        queryset = queryset.annotate(
            _latest_status=Subquery(latest_cs.values('status')[:1]),
            _latest_updated_at=Subquery(latest_cs.values('updated_at')[:1]),
            _idle_duration=Case(
                When(_latest_status__in=inactive, then=None),
                default=ExpressionWrapper(
                    Now() - F('_latest_updated_at'),
                    output_field=DurationField(),
                ),
                output_field=DurationField(),
            ),
        )
        if ordering_param == 'days_since_updated':
            queryset = queryset.order_by(F('_idle_duration').asc(nulls_last=True))
        else:
            queryset = queryset.order_by(F('_idle_duration').desc(nulls_last=True))
    else:
        queryset = queryset.order_by('-id')

    return queryset


@api_view(['GET'])
@permission_classes([AllowAny])
def user_kit_detail_view(request, username, kit_id):
    user = get_object_or_404(User, username=username, is_active=True)
    kit = get_object_or_404(
        Kit.objects
        .select_related('brand__maker', 'brand', 'scale', 'owner')
        .prefetch_related('tags', 'creationstatus_set'),
        pk=kit_id,
        owner=user,
    )
    serializer = KitSerializer(kit, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def user_kits_view(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    queryset = (
        Kit.objects
        .filter(owner=user)
        .select_related('brand__maker', 'brand', 'scale', 'owner')
        .prefetch_related('tags', 'creationstatus_set')
    )
    queryset = _apply_kit_filters(queryset, request.query_params)

    paginator = KitPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = KitSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def user_summary_view(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    s = CreationStatus.Status
    inactive = [s.SOLD, s.PARTED_OUT]

    excluded_ids = (
        CreationStatus.objects
        .filter(status__in=inactive)
        .values_list('kit_id', flat=True)
        .distinct()
    )
    active = Kit.objects.filter(owner=user).exclude(pk__in=excluded_ids)

    top_tags = list(
        Tag.objects
        .annotate(kit_count=Count(
            'kits',
            filter=Q(kits__owner=user) & ~Q(kits__id__in=excluded_ids),
        ))
        .filter(kit_count__gt=0)
        .order_by('-kit_count')
        .values('id', 'name', 'kit_count')[:5]
    )

    backlog_qs     = active.filter(creationstatus__status=s.BACKLOG).distinct()
    in_progress_qs = active.filter(creationstatus__status=s.IN_PROGRESS).distinct()
    completed_qs   = active.filter(creationstatus__status=s.COMPLETED).distinct()

    def price_sum(qs):
        return int(qs.aggregate(total=Sum('price'))['total'] or 0)

    return Response({
        'username':          username,
        'total_kits':        active.count(),
        'backlog':           backlog_qs.count(),
        'in_progress':       in_progress_qs.count(),
        'completed':         completed_qs.count(),
        'total_price':       price_sum(active),
        'backlog_price':     price_sum(backlog_qs),
        'in_progress_price': price_sum(in_progress_qs),
        'completed_price':   price_sum(completed_qs),
        'tags_top':          top_tags,
    })
