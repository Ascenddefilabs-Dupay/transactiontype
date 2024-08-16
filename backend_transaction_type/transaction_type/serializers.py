from rest_framework import serializers
from .models import Project , TransactionTable 
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'mobile_number', 'qr_code']





class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionTable
        fields = '__all__'


