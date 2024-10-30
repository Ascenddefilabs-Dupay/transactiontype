from rest_framework import serializers
from .models import  TransactionTable 
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'mobile_number', 'qr_code']



class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionTable
        fields = '__all__'


