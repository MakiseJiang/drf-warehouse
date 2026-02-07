from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Material, Transaction
from .serializers import MaterialSerializer, TransactionSerializer


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all().order_by('id')
    serializer_class = MaterialSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['material_id', 'name', 'model_number', 'usage', 'warehouse', 'shelf']


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().order_by('-date')
    serializer_class = TransactionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['transaction_type', 'material__name', 'material__material_id']

    def create(self, request, *args, **kwargs):
        # Override create to update material quantity
        response = super().create(request, *args, **kwargs)
        if response.status_code == 201:
            transaction = Transaction.objects.get(id=response.data['id'])
            material = transaction.material
            if transaction.transaction_type == 'IN':
                material.quantity += transaction.quantity
            elif transaction.transaction_type == 'OUT':
                material.quantity -= transaction.quantity
            material.save()
        return response