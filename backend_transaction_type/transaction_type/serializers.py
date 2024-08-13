from rest_framework import serializers
from .models import Project , TransactionTable ,WalletTable ,Address ,AddressBasedTransaction
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


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTable
        fields = '__all__'


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class AddressBasedTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressBasedTransaction
        fields = ['transaction_type', 'transaction_amount', 'transaction_currency', 'transaction_status', 'fiat_address']

    def validate(self, data):
        # Custom validation logic
        # Ensure fiat_address exists in the Address table
        fiat_address = data.get('fiat_address')
        if not Address.objects.filter(fiat_address=fiat_address).exists():
            raise serializers.ValidationError("Invalid fiat address.")
        return data