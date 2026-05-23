from rest_framework import serializers
from .models import Maker, Brand, Scale, Tag, Kit, CreationStatus


class MakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maker
        fields = ['id', 'name', 'image', 'description']


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'image', 'maker', 'description']


class ScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scale
        fields = ['id', 'size', 'description']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class KitSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    maker_name = serializers.CharField(source='brand.maker.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    scale_size = serializers.CharField(source='scale.size', read_only=True)

    class Meta:
        model = Kit
        fields = [
            'id', 'name',
            'maker_name',
            'brand', 'brand_name',
            'scale', 'scale_size',
            'price', 'image', 'description',
            'tags', 'tag_ids',
        ]

    def create(self, validated_data):
        tag_objs = validated_data.pop('tag_ids', [])
        kit = Kit.objects.create(**validated_data)
        kit.tags.set(tag_objs)
        return kit

    def update(self, instance, validated_data):
        tag_objs = validated_data.pop('tag_ids', None)
        instance = super().update(instance, validated_data)
        if tag_objs is not None:
            instance.tags.set(tag_objs)
        return instance


class CreationStatusSerializer(serializers.ModelSerializer):
    get_date = serializers.DateField(required=False)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = CreationStatus
        fields = ['id', 'kit', 'get_date', 'status', 'status_display', 'description']
