import uuid
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Maker(models.Model):
    name = models.CharField(verbose_name="name", max_length=100)
    image = models.CharField(verbose_name="Image", max_length=255, null=True, blank=True)
    description = models.TextField(verbose_name="Description", null=True, blank=True)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(verbose_name="name", max_length=100)
    image = models.CharField(verbose_name="Image", max_length=255, null=True, blank=True)
    maker = models.ForeignKey(Maker, verbose_name="maker", on_delete=models.CASCADE)
    description = models.TextField(verbose_name="Description", null=True, blank=True)

    def __str__(self):
        return self.name


class Scale(models.Model):
    size = models.CharField(verbose_name="size", max_length=100)
    description = models.TextField(verbose_name="Description", null=True, blank=True)

    def __str__(self):
        return self.size


class Tag(models.Model):
    name = models.CharField(verbose_name="name", max_length=50, unique=True)

    def __str__(self):
        return self.name


class Kit(models.Model):
    name = models.CharField(verbose_name="name", max_length=100)
    brand = models.ForeignKey(Brand, verbose_name="brand", on_delete=models.CASCADE)
    scale = models.ForeignKey(Scale, verbose_name="scale", on_delete=models.CASCADE)
    price = models.DecimalField(verbose_name="price", max_digits=8, decimal_places=0)
    image = models.ImageField(verbose_name="image", upload_to='kits/', null=True, blank=True)
    description = models.TextField(verbose_name="Description", null=True, blank=True)
    tags = models.ManyToManyField(Tag, verbose_name="tags", blank=True, related_name="kits")
    owner = models.ForeignKey(
        User, verbose_name="owner", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="kits",
    )

    def __str__(self):
        return self.name


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verification_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.token}"


class FavoriteMaker(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_makers')
    maker = models.ForeignKey(Maker, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        unique_together = ('user', 'maker')


class FavoriteBrand(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_brands')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        unique_together = ('user', 'brand')


class CreationStatus(models.Model):
    class Status(models.TextChoices):
        BACKLOG = 'backlog', '積み'
        IN_PROGRESS = 'in_progress', '製作中'
        COMPLETED = 'completed', '完成'
        ON_HOLD = 'on_hold', '中断'
        SOLD = 'sold', '売却済み'
        PARTED_OUT = 'parted_out', '素材化'

    kit = models.ForeignKey(Kit, verbose_name="kit", on_delete=models.CASCADE)
    get_date = models.DateField(verbose_name="get_date", default=timezone.localdate)
    status = models.CharField(
        verbose_name="status",
        max_length=20,
        choices=Status.choices,
        default=Status.BACKLOG,
    )
    description = models.TextField(verbose_name="Description", null=True, blank=True)
    updated_at = models.DateTimeField(verbose_name="updated_at", auto_now=True)

    def __str__(self):
        return self.status
