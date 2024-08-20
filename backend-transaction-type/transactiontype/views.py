from django.shortcuts import render
from rest_framework import viewsets
from .models import Project ,TransactionTable 
from .serializers import ProjectSerializer ,TransactionSerializer 
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
        cursor.execute("SELECT * FROM currency_converter_fiatwallet")
        rows = cursor.fetchall()

    receiver_numbers = []
    wallet_ids = []
    for i in rows:
        receiver_numbers.append(i[2])
        wallet_ids.append(i[0])
    print(wallet_ids)

    def create(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM currency_converter_fiatwallet")
            rows = cursor.fetchall()
        print(rows[-1])
        try:
            wallet_id = rows[-1][0]
            sender_mobile_number = rows[-1][7]
            amount = rows[-1][4]
            currncy_type = rows[-1][2]

            receiver_numbers = []
            wallet_ids = []
            wallet_amount = []
            for i in rows:
                receiver_numbers.append(i[7])
                wallet_ids.append(i[0])
                wallet_amount.append(i[4])
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
                                "UPDATE currency_converter_fiatwallet SET fiat_wallet_balance = %s WHERE fiat_wallet_id = %s",
                                [deducted_amount, wallet_id]
                            )
                    with connection.cursor() as cursor:
                            cursor.execute(
                                "UPDATE currency_converter_fiatwallet SET fiat_wallet_balance = %s WHERE fiat_wallet_id = %s",
                                [credit_amount, wallet_ids[index]]
                            )
                    return super().create(request, *args, **kwargs) 
                else:
                    return JsonResponse({'status': 'failure', 'message': 'Payment Failure'})

        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class QRViewSet(viewsets.ModelViewSet):
    queryset = TransactionTable.objects.all()
    serializer_class = TransactionSerializer
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM currency_converter_fiatwallet")
        rows = cursor.fetchall()

    receiver_numbers = []
    wallet_ids = []
    for i in rows:
        receiver_numbers.append(i[7])
        wallet_ids.append(i[0])
    print(wallet_ids)

    def create(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM currency_converter_fiatwallet")
            rows = cursor.fetchall()
        print(rows[-1])
        try:
            wallet_id = rows[-1][0]
            sender_mobile_number = rows[-1][7]
            amount = rows[-1][4]
            currncy_type = rows[-1][2]

            receiver_numbers = []
            wallet_ids = []
            wallet_amount = []
            for i in rows:
                receiver_numbers.append(i[7])
                wallet_ids.append(i[0])
                wallet_amount.append(i[4])
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
                                "UPDATE currency_converter_fiatwallet SET fiat_wallet_balance = %s WHERE fiat_wallet_id = %s",
                                [deducted_amount, wallet_id]
                            )
                    with connection.cursor() as cursor:
                            cursor.execute(
                                "UPDATE currency_converter_fiatwallet SET fiat_wallet_balance = %s WHERE fiat_wallet_id = %s",
                                [credit_amount, wallet_ids[index]]
                            )
                    return super().create(request, *args, **kwargs) 
                else:
                    return JsonResponse({'status': 'failure', 'message': 'Payment Failure'})

        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        




class FiatAddressViewSet(viewsets.ModelViewSet):
    queryset = TransactionTable.objects.all()
    serializer_class = TransactionSerializer

    def create(self, request, *args, **kwargs):
        fiat_address = request.data.get('fiat_address')
        transaction_amount = float(request.data.get('transaction_amount'))
        transaction_currency = request.data.get('transaction_currency')

        # Fetch wallet info based on fiat address
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM currency_converter_fiatwallet WHERE fiat_wallet_address = %s", [fiat_address])
            rows = cursor.fetchall()

        if not rows:
            return JsonResponse({'status': 'address_failure', 'message': 'Fiat Address does not exist.'})

        try:
            # Process the wallet associated with the fiat address
            wallet_row = rows[0]  # Assuming there's only one row for the fiat address
            wallet_id = wallet_row[0]  # Wallet ID is in column 1
            wallet_amount = float(wallet_row[4])  # Ensure this column exists and holds the wallet amount
            wallet_currency = wallet_row[2]  # Currency type is in column 4 (adjust if necessary)

            # Currency validation
            if wallet_currency != transaction_currency:
                return JsonResponse({'status': 'currency_failure', 'message': 'Currency must be the same.'})

            # Fetch the last row of the wallet table
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM currency_converter_fiatwallet ORDER BY fiat_wallet_id DESC LIMIT 1")
                last_row = cursor.fetchone()

            if not last_row:
                return JsonResponse({'status': 'failure', 'message': 'No wallet records found.'})

            last_wallet_id = last_row[0]  # Wallet ID in the last row
            last_wallet_amount = float(last_row[4])  # Amount in the last row

            # Validate if transaction amount is less than or equal to the last wallet amount
            if transaction_amount > last_wallet_amount:
                return JsonResponse({'status': 'failure', 'message': 'Insufficient funds in the last wallet row.'})

            # Add the transaction amount to the wallet associated with the fiat address
            updated_wallet_amount = wallet_amount + transaction_amount
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE currency_converter_fiatwallet SET fiat_wallet_balance = %s WHERE fiat_wallet_id = %s",
                    [updated_wallet_amount, wallet_id]
                )

            # Deduct the transaction amount from the last wallet row
            updated_last_wallet_amount = last_wallet_amount - transaction_amount
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE currency_converter_fiatwallet SET fiat_wallet_balance = %s WHERE fiat_wallet_id = %s",
                    [updated_last_wallet_amount, last_wallet_id]
                )

            # Proceed with creating the transaction record
            return super().create(request, *args, **kwargs)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
