from django.db import models, transaction


class Product(models.Model):
    purchase_date = models.DateField(verbose_name='購入日')
    product_name = models.CharField(max_length=255, verbose_name='商品名')
    price = models.DecimalField(max_digits=9, decimal_places=0, verbose_name='価格')
    creation_status = models.CharField(max_length=50, verbose_name='積み状況')

    def __str__(self):
        return self.product_name
