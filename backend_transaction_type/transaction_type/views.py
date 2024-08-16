from django.shortcuts import render
from rest_framework import viewsets
from .models import Project ,TransactionTable ,WalletTable ,Address,AddressBasedTransaction
from .serializers import ProjectSerializer ,TransactionSerializer ,WalletSerializer ,AddressSerializer ,AddressBasedTransactionSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import User
from .serializers import UserSerializer
from rest_framework.views import APIView
from django.db import connection
from django.http import JsonResponse

class UserRegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        name = request.data.get('name')
        mobile_number = request.data.get('mobile_number')

        if not name or not mobile_number:
            return Response({"error": "Name and mobile number are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user and generate the QR code
        user = User.objects.create(name=name, mobile_number=mobile_number)
        user.generate_qr_code()

        return Response({"message": "User registered successfully", "qr_code": user.qr_code}, status=status.HTTP_201_CREATED)
    
class QRCodeListView(APIView):
    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



# Create your views here.

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = TransactionTable.objects.all()
    serializer_class = TransactionSerializer
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM wallet_table")
        rows = cursor.fetchall()

    receiver_numbers = []
    wallet_ids = []
    for i in rows:
        receiver_numbers.append(i[2])
        wallet_ids.append(i[1])
    print(wallet_ids)

    def create(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM wallet_table")
            rows = cursor.fetchall()
        print(rows[-1])
        try:
            wallet_id = rows[-1][1]
            sender_mobile_number = rows[-1][2]
            amount = rows[-1][3]
            currncy_type = rows[-1][4]

            receiver_numbers = []
            wallet_ids = []
            wallet_amount = []
            for i in rows:
                receiver_numbers.append(i[2])
                wallet_ids.append(i[1])
                wallet_amount.append(i[3])
            index = 0
            if wallet_id and sender_mobile_number:
                request.data['wallet_id'] = wallet_id
                request.data['sender_mobile_number'] = sender_mobile_number
            print(request.data.get('transaction_amount'), type(request.data.get('transaction_amount')))

            if (request.data['user_phone_number'] in receiver_numbers):
                index = receiver_numbers.index(request.data['user_phone_number'])
            
            if request.data['user_phone_number'] not in receiver_numbers:
                print(request.data['user_phone_number'])
                return JsonResponse({'status': 'mobile_failure', 'message': 'Mobile Number Failure'})
            elif currncy_type != request.data['transaction_currency']:
                return JsonResponse({'status': 'currency_failure', 'message': 'Currency must be same'})
            
            else:
                if float(request.data.get('transaction_amount')) < float(amount):
                    deducted_amount = float(amount) - float(request.data.get('transaction_amount'))
                    credit_amount = float(wallet_amount[index]) + float(request.data.get('transaction_amount'))
                    print(wallet_ids[index], credit_amount)
                    with connection.cursor() as cursor:
                            cursor.execute(
                                "UPDATE wallet_table SET amount = %s WHERE wallet_id = %s",
                                [deducted_amount, wallet_id]
                            )
                    with connection.cursor() as cursor:
                            cursor.execute(
                                "UPDATE wallet_table SET amount = %s WHERE wallet_id = %s",
                                [credit_amount, wallet_ids[index]]
                            )
                    return super().create(request, *args, **kwargs) 
                else:
                    return JsonResponse({'status': 'failure', 'message': 'Payment Failure'})

        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class WalletViewSet(viewsets.ModelViewSet):
    queryset = WalletTable.objects.all()
    serializer_class = WalletSerializer


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer


class AddressBasedTransactionViewSet(viewsets.ModelViewSet):
    queryset = AddressBasedTransaction.objects.all()
    serializer_class = AddressBasedTransactionSerializer


    def create(self, request, *args, **kwargs):
        fiat_address = request.data.get('fiat_address')

        # Check if the fiat_address exists in the Address model
        if not Address.objects.filter(fiat_address=fiat_address).exists():
            return Response(
                {"detail": "Fiat address not found."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate and save the transaction data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def create(self, request, *args, **kwargs):
    #     fiat_address = request.data.get('fiat_address')
        
    #     # Check if the fiat address exists in the Address table
    #     if not Address.objects.filter(fiat_address=fiat_address).exists():
    #         return Response(
    #             {'detail': 'Fiat address does not exist in the address table.'},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
        
    #     # If the fiat address exists, proceed with creating the transaction
    #     return super().create(request, *args, **kwargs)

class QRViewSet(viewsets.ModelViewSet):
    queryset = TransactionTable.objects.all()
    serializer_class = TransactionSerializer
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM wallet_table")
        rows = cursor.fetchall()

    receiver_numbers = []
    wallet_ids = []
    for i in rows:
        receiver_numbers.append(i[2])
        wallet_ids.append(i[1])
    print(wallet_ids)

    def create(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM wallet_table")
            rows = cursor.fetchall()
        print(rows[-1])
        try:
            wallet_id = rows[-1][1]
            sender_mobile_number = rows[-1][2]
            amount = rows[-1][3]
            currncy_type = rows[-1][4]

            receiver_numbers = []
            wallet_ids = []
            wallet_amount = []
            for i in rows:
                receiver_numbers.append(i[2])
                wallet_ids.append(i[1])
                wallet_amount.append(i[3])
            index = 0
            if wallet_id and sender_mobile_number:
                request.data['wallet_id'] = wallet_id
                request.data['sender_mobile_number'] = sender_mobile_number
            print(request.data.get('transaction_amount'), type(request.data.get('transaction_amount')))

            if (request.data['user_phone_number'] in receiver_numbers):
                index = receiver_numbers.index(request.data['user_phone_number'])
            
            if request.data['user_phone_number'] not in receiver_numbers:
                print(request.data['user_phone_number'])
                return JsonResponse({'status': 'mobile_failure', 'message': 'Mobile Number Failure'})
            elif currncy_type != request.data['transaction_currency']:
                return JsonResponse({'status': 'currency_failure', 'message': 'Currency must be same'})
            
            else:
                if float(request.data.get('transaction_amount')) < float(amount):
                    deducted_amount = float(amount) - float(request.data.get('transaction_amount'))
                    credit_amount = float(wallet_amount[index]) + float(request.data.get('transaction_amount'))
                    print(wallet_ids[index], credit_amount)
                    with connection.cursor() as cursor:
                            cursor.execute(
                                "UPDATE wallet_table SET amount = %s WHERE wallet_id = %s",
                                [deducted_amount, wallet_id]
                            )
                    with connection.cursor() as cursor:
                            cursor.execute(
                                "UPDATE wallet_table SET amount = %s WHERE wallet_id = %s",
                                [credit_amount, wallet_ids[index]]
                            )
                    return super().create(request, *args, **kwargs) 
                else:
                    return JsonResponse({'status': 'failure', 'message': 'Payment Failure'})

        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)