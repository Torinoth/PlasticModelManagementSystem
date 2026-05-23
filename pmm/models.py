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
    image = models.CharField(verbose_name="image", max_length=255, null=True, blank=True)
    description = models.TextField(verbose_name="Description", null=True, blank=True)
    tags = models.ManyToManyField(Tag, verbose_name="tags", blank=True, related_name="kits")

    def __str__(self):
        return self.name


class CreationStatus(models.Model):
    class Status(models.TextChoices):
        BACKLOG = 'backlog', '積み'
        IN_PROGRESS = 'in_progress', '製作中'
        COMPLETED = 'completed', '完成'
        ON_HOLD = 'on_hold', '中断'

    kit = models.ForeignKey(Kit, verbose_name="kit", on_delete=models.CASCADE)
    get_date = models.DateField(verbose_name="get_date", default=timezone.localdate)
    status = models.CharField(
        verbose_name="status",
        max_length=20,
        choices=Status.choices,
        default=Status.BACKLOG,
    )
    description = models.TextField(verbose_name="Description", null=True, blank=True)

    def __str__(self):
        return self.status
