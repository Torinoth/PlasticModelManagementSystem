from django.utils import timezone
from rest_framework import serializers
from .models import Maker, Brand, Scale, Tag, Kit, CreationStatus


class MakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maker
        fields = ['id', 'name', 'image', 'description']


class BrandSerializer(serializers.ModelSerializer):
    maker_name = serializers.CharField(source='maker.name', read_only=True)

    class Meta:
        model = Brand
        fields = ['id', 'name', 'image', 'maker', 'maker_name', 'description']


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
    image = serializers.ImageField(required=False, allow_null=True, use_url=False)
    status = serializers.SerializerMethodField()
    days_since_updated = serializers.SerializerMethodField()

    class Meta:
        model = Kit
        fields = [
            'id', 'name',
            'maker_name',
            'brand', 'brand_name',
            'scale', 'scale_size',
            'price', 'image', 'description',
            'tags', 'tag_ids',
            'status', 'days_since_updated',
        ]

    def get_status(self, obj):
        cs = obj.creationstatus_set.order_by('-id').first()
        return cs.status if cs else None

    def get_days_since_updated(self, obj):
        inactive = {
            CreationStatus.Status.COMPLETED,
            CreationStatus.Status.SOLD,
            CreationStatus.Status.PARTED_OUT,
        }
        cs = obj.creationstatus_set.order_by('-id').first()
        if cs is None or cs.status in inactive or cs.updated_at is None:
            return None
        return (timezone.now().date() - cs.updated_at.date()).days

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.image:
            rep['image'] = instance.image.url
        return rep

    def to_internal_value(self, data):
        result = super().to_internal_value(data)
        status_value = data.get('status')
        if status_value:
            valid = [s[0] for s in CreationStatus.Status.choices]
            if status_value in valid:
                result['status'] = status_value
        return result

    def create(self, validated_data):
        tag_objs = validated_data.pop('tag_ids', [])
        status = validated_data.pop('status', CreationStatus.Status.BACKLOG)
        kit = Kit.objects.create(**validated_data)
        kit.tags.set(tag_objs)
        CreationStatus.objects.create(kit=kit, status=status)
        return kit

    def update(self, instance, validated_data):
        tag_objs = validated_data.pop('tag_ids', None)
        status = validated_data.pop('status', None)
        instance = super().update(instance, validated_data)
        if tag_objs is not None:
            instance.tags.set(tag_objs)
        if status is not None:
            cs = instance.creationstatus_set.order_by('-id').first()
            if cs:
                cs.status = status
                cs.save()
            else:
                CreationStatus.objects.create(kit=instance, status=status)
        return instance


class CreationStatusSerializer(serializers.ModelSerializer):
    get_date = serializers.DateField(required=False)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = CreationStatus
        fields = ['id', 'kit', 'get_date', 'status', 'status_display', 'description']
