from django.db import models


class Material(models.Model):
    material_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    model_number = models.CharField(max_length=200, blank=True, default='')
    category = models.CharField(max_length=100)
    equipment = models.CharField(max_length=200, blank=True, default='')
    warehouse = models.CharField(max_length=100, blank=True, default='')
    shelf = models.CharField(max_length=100, blank=True, default='')
    quantity = models.IntegerField()
    threshold = models.IntegerField(default=10)

    def __str__(self):
        return f"{self.material_id} - {self.name}"


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('IN', 'Inbound'),
        ('OUT', 'Outbound'),
    )
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_type} - {self.material.name} - {self.quantity}"