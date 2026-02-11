import json
import os
from django.conf import settings
from rest_framework import viewsets, filters, status
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


class SystemSettingsViewSet(viewsets.ViewSet):
    """
    ViewSet for system settings and maintenance.
    """
    
    @action(detail=False, methods=['get', 'post'])
    def warehouses(self, request):
        file_path = os.path.join(settings.BASE_DIR, 'frontend', 'src', 'config', 'warehouses.json')
        
        if request.method == 'GET':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return Response(data)
            except FileNotFoundError:
                return Response([], status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        elif request.method == 'POST':
            try:
                warehouses = request.data.get('warehouses', [])
                if not isinstance(warehouses, list):
                    return Response({'error': 'Invalid format, expected a list of strings.'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(warehouses, f, ensure_ascii=False, indent=2)
                
                return Response({'status': 'success', 'warehouses': warehouses})
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def clear_zero_stock(self, request):
        """Delete all materials with quantity <= 0"""
        try:
            count, _ = Material.objects.filter(quantity__lte=0).delete()
            return Response({'status': 'success', 'deleted_count': count})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)