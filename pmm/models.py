from django.db import models


class PlasticModel(models.Model):
    name = models.CharField(max_length=255)
    scale = models.CharField(max_length=50)
    brand = models.CharField(max_length=255)
    stock = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
