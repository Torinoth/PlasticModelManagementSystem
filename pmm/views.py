from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from .models import Maker, Brand, Scale, Tag, Kit, CreationStatus
from .serializers import (
    MakerSerializer, BrandSerializer, ScaleSerializer,
    TagSerializer, KitSerializer, CreationStatusSerializer,
)


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
        queryset = Kit.objects.select_related('maker', 'brand', 'scale').prefetch_related('tags')
        tags_param = self.request.query_params.get('tags')
        if tags_param:
            tag_ids = [int(t) for t in tags_param.split(',') if t.strip().isdigit()]
            if tag_ids:
                queryset = queryset.filter(tags__id__in=tag_ids).distinct()
        return queryset


class CreationStatusViewSet(viewsets.ModelViewSet):
    queryset = CreationStatus.objects.all()
    serializer_class = CreationStatusSerializer
