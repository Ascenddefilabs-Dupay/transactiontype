from rest_framework import serializers
from .models import Project , TransactionTable

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionTable
        fields = '__all__'