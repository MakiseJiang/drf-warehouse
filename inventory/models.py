from django.db import models


class Material(models.Model):
    material_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    model_number = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    equipment = models.CharField(max_length=200)
    warehouse = models.CharField(max_length=100)
    shelf = models.CharField(max_length=100)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.material_id} - {self.name}"