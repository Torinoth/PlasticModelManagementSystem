from django.db import models


class brand(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class scale(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class PlasticModel(models.Model):
    name = models.CharField(max_length=255)
    scale = models.ForeignKey(scale, on_delete=models.CASCADE)
    brand = models.ForeignKey(brand, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class stock_history(models.Model):
    model = models.ForeignKey(PlasticModel, on_delete=models.CASCADE)
    quantity_before = models.IntegerField()
    quantity_after = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.model.name} {self.quantity_before} -> {self.quantity_after}'

def add_stock(plastic_model, quantity):
    plastic_model.stock += quantity
    plastic_model.save()
    stock_history.objects.create(model=plastic_model,
                                 quantity_before=plastic_model.stock - quantity,
                                 quantity_after=plastic_model.stock)

def remove_stock(plastic_model, quantity):
    plastic_model.stock -= quantity
    plastic_model.save()
    stock_history.objects.create(model=plastic_model,
                                 quantity_before=plastic_model.stock + quantity,
                                 quantity_after=plastic_model.stock)
