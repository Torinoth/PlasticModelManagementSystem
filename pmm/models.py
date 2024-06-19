from django.db import models


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


class Product(models.Model):
    name = models.CharField(verbose_name="name", max_length=100)
    maker = models.ForeignKey(Maker, verbose_name="maker", on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, verbose_name="brand", on_delete=models.CASCADE)
    scale = models.ForeignKey(Scale, verbose_name="scale", on_delete=models.CASCADE)
    price = models.DecimalField(verbose_name="price", max_digits=5, decimal_places=2)
    image = models.CharField(verbose_name="image", max_length=255, null=True, blank=True)
    description = models.TextField(verbose_name="Description", null=True, blank=True)

    def __str__(self):
        return self.name


class CreationStatus(models.Model):
    product = models.ForeignKey(Product, verbose_name="product", on_delete=models.CASCADE)
    get_date = models.DateField(verbose_name="get_date", auto_now=False, auto_now_add=True)
    status = models.CharField(verbose_name="status", max_length=100)
    description = models.TextField(verbose_name="Description", null=True, blank=True)

    def __str__(self):
        return self.status
