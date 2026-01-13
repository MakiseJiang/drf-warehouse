from rest_framework import serializers
from .models import Material, Transaction


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    material_name = serializers.ReadOnlyField(source='material.name')
    material_code = serializers.ReadOnlyField(source='material.material_id')

    class Meta:
        model = Transaction
        fields = '__all__'