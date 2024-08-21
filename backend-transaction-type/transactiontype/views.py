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

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM user_currencies")
            currency_rows = cursor.fetchall()
        
        currency_wallet_id = []
        currency_type_list = []
        balance = []
        for i in currency_rows:
            currency_wallet_id.append(i[1])
            currency_type_list.append(i[2])
            balance.append(i[3])

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
        
            else:
                user_currency_id_list = []
                a = -1
                reciever_wallet_amont = []
                validation_list = []
                for i in currency_wallet_id:
                    a += 1
                    if wallet_ids[index] == currency_wallet_id[a] and request.data.get('transaction_currency') == currency_type_list[a]:
                        print(a)
                        user_currency_id_list.append(currency_type_list[a])
                        reciever_wallet_amont.append(balance[a])
                        
                    if wallet_id == currency_wallet_id[a] and request.data.get('transaction_currency') == currency_type_list[a]:
                        print(a)
                        validation_list.append(currency_type_list[a])

                print(user_currency_id_list, reciever_wallet_amont)

                if wallet_id in currency_wallet_id and wallet_ids[index] in currency_wallet_id:
                    currncy_index = currency_wallet_id.index(wallet_id)
                    if request.data.get('transaction_currency') in set(user_currency_id_list) and wallet_ids[index] in currency_wallet_id:
                        currncy_index1 = currency_wallet_id.index(wallet_ids[index])

                    
                    if len(validation_list) == 0:
                        return JsonResponse({'status': 'curreny_error', 'message': 'Payment Failure'}) 


                    if float(request.data.get('transaction_amount')) <= float(balance[currncy_index]) and len(user_currency_id_list) >= 1:
                        deducted_amount = float(balance[currncy_index]) - float(request.data.get('transaction_amount'))
                        credit_amount = float(reciever_wallet_amont[0]) + float(request.data.get('transaction_amount'))
                        print(wallet_ids[index], credit_amount, deducted_amount)
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "UPDATE user_currencies SET balance = %s WHERE wallet_id = %s",
                                [deducted_amount, currency_wallet_id[currncy_index]]
                            )
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "UPDATE user_currencies SET balance = %s WHERE wallet_id = %s AND currency_type = %s",
                                [credit_amount, currency_wallet_id[currncy_index1], request.data.get('transaction_currency')]
                            )
                        return super().create(request, *args, **kwargs) 
                    elif float(request.data.get('transaction_amount')) <= float(balance[currncy_index]) and len(user_currency_id_list) < 1 :
                        deducted_amount = float(balance[currncy_index]) - float(request.data.get('transaction_amount'))
                        credit_amount = float(request.data.get('transaction_amount'))
                        print(wallet_ids[index], credit_amount, deducted_amount)
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "UPDATE user_currencies SET balance = %s WHERE wallet_id = %s",
                                [deducted_amount, currency_wallet_id[currncy_index]]
                            )
                        with connection.cursor() as cursor:
                            cursor.execute(
                                """
                                INSERT INTO user_currencies (wallet_id, currency_type, balance)
                                VALUES (%s, %s, %s)
                                """,
                                [wallet_ids[index], currency_type_list[currncy_index], float(request.data.get('transaction_amount'))]
                            )

                        return super().create(request, *args, **kwargs)
                    else:
                       return JsonResponse({'status': 'insufficient_funds', 'message': 'Payment Failure'}) 
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

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM user_currencies")
            currency_rows = cursor.fetchall()
        
        currency_wallet_id = []
        currency_type_list = []
        balance = []
        for i in currency_rows:
            currency_wallet_id.append(i[1])
            currency_type_list.append(i[2])
            balance.append(i[3])
            
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
            
            else:
                user_currency_id_list = []
                a = -1
                reciever_wallet_amont = []
                validation_list = []
                for i in currency_wallet_id:
                    a += 1
                    if wallet_ids[index] == currency_wallet_id[a] and request.data.get('transaction_currency') == currency_type_list[a]:
                        print(a)
                        user_currency_id_list.append(currency_type_list[a])
                        reciever_wallet_amont.append(balance[a])
                        
                    if wallet_id == currency_wallet_id[a] and request.data.get('transaction_currency') == currency_type_list[a]:
                        print(a)
                        validation_list.append(currency_type_list[a])
                        

                        

                print(user_currency_id_list, reciever_wallet_amont)

                if wallet_id in currency_wallet_id and wallet_ids[index] in currency_wallet_id:
                    currncy_index = currency_wallet_id.index(wallet_id)
                    if request.data.get('transaction_currency') in set(user_currency_id_list) and wallet_ids[index] in currency_wallet_id:
                        currncy_index1 = currency_wallet_id.index(wallet_ids[index])

                    
                    if len(validation_list) == 0:
                        return JsonResponse({'status': 'curreny_error', 'message': 'Payment Failure'}) 


                    if float(request.data.get('transaction_amount')) <= float(balance[currncy_index]) and len(user_currency_id_list) >= 1:
                        deducted_amount = float(balance[currncy_index]) - float(request.data.get('transaction_amount'))
                        credit_amount = float(reciever_wallet_amont[0]) + float(request.data.get('transaction_amount'))
                        print(wallet_ids[index], credit_amount, deducted_amount)
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "UPDATE user_currencies SET balance = %s WHERE wallet_id = %s",
                                [deducted_amount, currency_wallet_id[currncy_index]]
                            )
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "UPDATE user_currencies SET balance = %s WHERE wallet_id = %s AND currency_type = %s",
                                [credit_amount, currency_wallet_id[currncy_index1], request.data.get('transaction_currency')]
                            )
                        return super().create(request, *args, **kwargs) 
                    elif float(request.data.get('transaction_amount')) <= float(balance[currncy_index]) and len(user_currency_id_list) < 1 :
                        deducted_amount = float(balance[currncy_index]) - float(request.data.get('transaction_amount'))
                        credit_amount = float(request.data.get('transaction_amount'))
                        print(wallet_ids[index], credit_amount, deducted_amount)
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "UPDATE user_currencies SET balance = %s WHERE wallet_id = %s",
                                [deducted_amount, currency_wallet_id[currncy_index]]
                            )
                        with connection.cursor() as cursor:
                            cursor.execute(
                                """
                                INSERT INTO user_currencies (wallet_id, currency_type, balance)
                                VALUES (%s, %s, %s)
                                """,
                                [wallet_ids[index], currency_type_list[currncy_index], float(request.data.get('transaction_amount'))]
                            )

                        return super().create(request, *args, **kwargs)
                    else:
                       return JsonResponse({'status': 'insufficient_funds', 'message': 'Payment Failure'}) 
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
            fiat_wallet = cursor.fetchone()

        if not fiat_wallet:
            return JsonResponse({'status': 'address_failure', 'message': 'Fiat Address does not exist.'})

        try:
            # Fetch the last row of the wallet table
            with connection.cursor() as cursor:
                cursor.execute("SELECT fiat_wallet_id FROM currency_converter_fiatwallet ORDER BY fiat_wallet_id DESC LIMIT 1")
                last_wallet = cursor.fetchone()

            if not last_wallet:
                return JsonResponse({'status': 'failure', 'message': 'No wallet records found.'})

            last_wallet_id = last_wallet[0]  # Wallet ID is in the first column

            # Check if the selected currency exists in the user_currencies table for the last wallet ID
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT balance FROM user_currencies WHERE wallet_id = %s AND currency_type = %s",
                    [last_wallet_id, transaction_currency]
                )
                currency_balance = cursor.fetchone()

            if not currency_balance:
                return JsonResponse({'status': 'currency_failuregi', 'message': 'Selected currency not found in the wallet.'})

            current_balance = float(currency_balance[0])

            # Validate if transaction amount is less than or equal to the current balance
            if transaction_amount > current_balance:
                return JsonResponse({'status': 'failure', 'message': 'Insufficient funds in the selected currency.'})

            # Deduct the transaction amount from the selected currency balance
            updated_balance = current_balance - transaction_amount
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE user_currencies SET balance = %s WHERE wallet_id = %s AND currency_type = %s",
                    [updated_balance, last_wallet_id, transaction_currency]
                )

            # Add the transaction amount to the fiat wallet's currency balance
            fiat_wallet_id = fiat_wallet[0]  # Wallet ID is in the first column
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT balance FROM user_currencies WHERE wallet_id = %s AND currency_type = %s",
                    [fiat_wallet_id, transaction_currency]
                )
                fiat_wallet_balance = cursor.fetchone()

            if fiat_wallet_balance:
                # Update existing row
                new_fiat_balance = float(fiat_wallet_balance[0]) + transaction_amount
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE user_currencies SET balance = %s WHERE wallet_id = %s AND currency_type = %s",
                        [new_fiat_balance, fiat_wallet_id, transaction_currency]
                    )
            else:
                # Insert new row
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO user_currencies (wallet_id, currency_type, balance) VALUES (%s, %s, %s)",
                        [fiat_wallet_id, transaction_currency, transaction_amount]
                    )

            # Proceed with creating the transaction record
            return super().create(request, *args, **kwargs)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
