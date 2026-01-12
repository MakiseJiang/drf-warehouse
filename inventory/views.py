from rest_framework import viewsets, filters
from .models import Material
from .serializers import MaterialSerializer


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all().order_by('id')
    serializer_class = MaterialSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['material_id', 'name', 'model_number', 'category', 'equipment', 'warehouse', 'shelf']