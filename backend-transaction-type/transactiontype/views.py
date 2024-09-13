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


from django.views import View
# class FetchQRCodeView(View):

#     def get(self, request, *args, **kwargs):
#         user_id = request.GET.get('user_id')  # Get user_id from query parameters
#         if not user_id:
#             return JsonResponse({'error': 'User ID is required.'}, status=400)

#         qr_code = None

#         try:
#             with connection.cursor() as cursor:
#                 # Query to fetch the qr_code from fiat_wallet table based on user_id
#                 cursor.execute("""
#                     SELECT qr_code 
#                     FROM fiat_wallet 
#                     WHERE user_id = %s
#                 """, [user_id])
#                 row = cursor.fetchone()

#                 if row:
#                     qr_code = row[0]  # Extract the QR code from the query result
#                 else:
#                     return JsonResponse({'error': 'QR code not found for this user ID.'}, status=404)

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)

#         return JsonResponse({'qr_code': qr_code})
    

# class FetchQRCodeView(View):

#     def get(self, request, *args, **kwargs):
#         user_id = request.GET.get('user_id')  # Get user_id from query parameters
#         if not user_id:
#             return JsonResponse({'error': 'User ID is required.'}, status=400)

#         qr_code = None
#         email = None
#         mobile_number = None

#         try:
#             with connection.cursor() as cursor:
#                 # Query to fetch the qr_code, email, and mobile number from fiat_wallet table based on user_id
#                 cursor.execute("""
#                     SELECT qr_code, fiat_wallet_email, fiat_wallet_phone_number 
#                     FROM fiat_wallet 
#                     WHERE user_id = %s
#                 """, [user_id])
#                 row = cursor.fetchone()

#                 if row:
#                     qr_code = row[0]  # Extract the QR code from the query result
#                     email = row[1]   # Extract the email
#                     mobile_number = row[2]  # Extract the mobile number
#                 else:
#                     return JsonResponse({'error': 'Details not found for this user ID.'}, status=404)

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)

#         return JsonResponse({'qr_code': qr_code, 'email': email, 'mobile_number': mobile_number})

class FetchQRCodeView(View):

    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id')  # Get user_id from query parameters
        if not user_id:
            return JsonResponse({'error': 'User ID is required.'}, status=400)

        qr_code = None
        email = None
        mobile_number = None
        first_name = None  # Variable to store the user's first name

        try:
            with connection.cursor() as cursor:
                # Query to fetch the qr_code, email, mobile number from fiat_wallet table 
                # and the user's name from the users table based on user_id
                cursor.execute("""
                    SELECT f.qr_code, f.fiat_wallet_email, f.fiat_wallet_phone_number, u.user_first_name
                    FROM fiat_wallet f
                    JOIN users u ON f.user_id = u.user_id
                    WHERE f.user_id = %s
                """, [user_id])
                
                row = cursor.fetchone()

                if row:
                    qr_code = row[0]  # Extract the QR code from the query result
                    email = row[1]    # Extract the email
                    mobile_number = row[2]  # Extract the mobile number
                    first_name = row[3]  # Extract the user's first name
                else:
                    return JsonResponse({'error': 'Details not found for this user ID.'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        return JsonResponse({
            'qr_code': qr_code,
            'email': email,
            'mobile_number': mobile_number,
            'first_name': first_name  # Send the first name to the frontend
        })



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

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')  # Fetch user_id from frontend

        # Fetch the corresponding wallet details for the given user_id
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM fiat_wallet WHERE user_id = %s", [user_id])
            user_wallet = cursor.fetchone()  # Get the row for the given user_id

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM user_currencies")
            currency_rows = cursor.fetchall()

        # Variables for storing currency and balance information
        currency_wallet_id = []
        currency_type_list = []
        balance = []
        for i in currency_rows:
            currency_wallet_id.append(i[1])
            currency_type_list.append(i[2])
            balance.append(i[3])

        try:
            if user_wallet:  # Ensure we have wallet data for the given user_id
                wallet_id = user_wallet[0]  # Get wallet_id from the user_wallet
                sender_mobile_number = user_wallet[7]  # Get mobile number

                # Process the transaction details
                request.data['wallet_id'] = wallet_id
                request.data['sender_mobile_number'] = sender_mobile_number

                # Fetch receiver details from fiat_wallet
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM fiat_wallet")
                    rows = cursor.fetchall()

                receiver_numbers = []
                wallet_ids = []
                wallet_amount = []
                for i in rows:
                    receiver_numbers.append(i[7])
                    wallet_ids.append(i[0])
                    wallet_amount.append(i[4])

                # Check if the provided phone number exists in receiver numbers
                if request.data['user_phone_number'] in receiver_numbers:
                    index = receiver_numbers.index(request.data['user_phone_number'])
                else:
                    return JsonResponse({'status': 'mobile_failure', 'message': 'Mobile Number Failure'})

                # Validate sender's wallet and currency details
                user_currency_id_list = []
                sender_wallet_amount = []
                receiver_wallet_amount = []
                validation_list = []

                for i in range(len(currency_wallet_id)):
                    if wallet_ids[index] == currency_wallet_id[i] and request.data.get('transaction_currency') == currency_type_list[i]:
                        user_currency_id_list.append(currency_type_list[i])
                        receiver_wallet_amount.append(balance[i])

                    if wallet_id == currency_wallet_id[i] and request.data.get('transaction_currency') == currency_type_list[i]:
                        validation_list.append(currency_type_list[i])
                        sender_wallet_amount.append(balance[i])

                # If no matching currency type for the sender's wallet, fail the transaction
                if len(validation_list) == 0:
                    return JsonResponse({'status': 'currency_error', 'message': 'Payment Failure'})

                # Check if the sender has sufficient funds
                if float(request.data.get('transaction_amount')) <= float(sender_wallet_amount[0]) and len(user_currency_id_list) >= 1:
                    # Deduct and credit amounts
                    deducted_amount = float(sender_wallet_amount[0]) - float(request.data.get('transaction_amount'))
                    credit_amount = float(receiver_wallet_amount[0]) + float(request.data.get('transaction_amount'))

                    # Update the sender's and receiver's balances in the user_currencies table
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "UPDATE user_currencies SET balance = %s WHERE wallet_id = %s AND currency_type = %s",
                            [deducted_amount, wallet_id, request.data.get('transaction_currency')]
                        )

                    with connection.cursor() as cursor:
                        cursor.execute(
                            "UPDATE user_currencies SET balance = %s WHERE wallet_id = %s AND currency_type = %s",
                            [credit_amount, wallet_ids[index], request.data.get('transaction_currency')]
                        )

                    return super().create(request, *args, **kwargs)

                # Case when user does not have the currency type, so we need to insert a new record
                elif float(request.data.get('transaction_amount')) <= float(sender_wallet_amount[0]) and len(user_currency_id_list) < 1:
                    deducted_amount = float(sender_wallet_amount[0]) - float(request.data.get('transaction_amount'))
                    credit_amount = float(request.data.get('transaction_amount'))

                    # Update the sender's balance and insert a new row for the receiver's currency
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "UPDATE user_currencies SET balance = %s WHERE wallet_id = %s AND currency_type = %s",
                            [deducted_amount, wallet_id, request.data.get('transaction_currency')]
                        )

                    with connection.cursor() as cursor:
                        cursor.execute(
                            """
                            INSERT INTO user_currencies (wallet_id, currency_type, balance)
                            VALUES (%s, %s, %s)
                            """,
                            [wallet_ids[index], request.data.get('transaction_currency'), credit_amount]
                        )

                    return super().create(request, *args, **kwargs)

                else:
                    return JsonResponse({'status': 'insufficient_funds', 'message': 'Payment Failure'})

            else:
                return JsonResponse({'status': 'failure', 'message': 'Invalid User ID'})

        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NumberTransactionValidationViewSet(viewsets.ModelViewSet):
    queryset = TransactionTable.objects.all()

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')  # Fetch user_id from frontend

        # Fetch the corresponding wallet details for the given user_id
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM fiat_wallet WHERE user_id = %s", [user_id])
            user_wallet = cursor.fetchone()  # Get the row for the given user_id

        if not user_wallet:
            return JsonResponse({'status': 'failure', 'message': 'Invalid User ID'})

        wallet_id = user_wallet[0]  # Get wallet_id from the user_wallet
        sender_mobile_number = user_wallet[7]  # Get mobile number

        # Fetch all rows from the user_currencies table
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM user_currencies")
            currency_rows = cursor.fetchall()

        # Fetch all rows from the fiat_wallet table to validate receiver's mobile number
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM fiat_wallet")
            receiver_rows = cursor.fetchall()

        receiver_numbers = [row[7] for row in receiver_rows]  # Extract receiver mobile numbers

        if request.data['user_phone_number'] not in receiver_numbers:
            return JsonResponse({'status': 'mobile_failure', 'message': 'Receiver mobile number not found'})

        # Initialize lists for currency details
        currency_wallet_id = []
        currency_type_list = []
        balance = []
        for row in currency_rows:
            currency_wallet_id.append(row[1])
            currency_type_list.append(row[2])
            balance.append(row[3])

        try:
            # Validate sender's wallet for the given currency type
            sender_wallet_amount = 0

            for i in range(len(currency_wallet_id)):
                if wallet_id == currency_wallet_id[i] and request.data.get('transaction_currency') == currency_type_list[i]:
                    sender_wallet_amount = balance[i]

            # Check if the sender has the selected currency
            if sender_wallet_amount == 0:
                return JsonResponse({'status': 'currency_error', 'message': 'Sender does not have the selected currency'})

            # Check if the sender has enough funds for the transaction
            if float(request.data.get('transaction_amount')) > float(sender_wallet_amount):
                return JsonResponse({'status': 'insufficient_funds', 'message': 'Insufficient funds in sender wallet'})

            # If validation passes
            return JsonResponse({'status': 'success', 'message': 'Validation passed'})

        except Exception as e:
            return Response({'error': 'An unexpected error occurred', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)







class QRValidationViewSet(viewsets.ViewSet):
    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')  # Fetch user_id from the request
        user_phone_number = request.data.get('user_phone_number')
        transaction_amount = float(request.data.get('transaction_amount'))
        transaction_currency = request.data.get('transaction_currency')

        # Fetch wallet details for the given user_id
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM fiat_wallet WHERE user_id = %s", [user_id])
            user_wallet = cursor.fetchone()

        if not user_wallet:
            return JsonResponse({'status': 'failure', 'message': 'Invalid User ID'})

        wallet_id = user_wallet[0]  # Get wallet_id from the user_wallet

        # Fetch all rows from the user_currencies table
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM user_currencies")
            currency_rows = cursor.fetchall()

        # Fetch all rows from the fiat_wallet table to validate receiver's mobile number
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM fiat_wallet")
            receiver_rows = cursor.fetchall()

        receiver_numbers = [row[7] for row in receiver_rows]  # Extract receiver mobile numbers

        if user_phone_number not in receiver_numbers:
            return JsonResponse({'status': 'mobile_failure', 'message': 'Receiver mobile number not found'})

        # Initialize lists for currency details
        currency_wallet_id = []
        currency_type_list = []
        balance = []

        for row in currency_rows:
            currency_wallet_id.append(row[1])
            currency_type_list.append(row[2])
            balance.append(row[3])

        try:
            # Validate sender's wallet for the given currency type
            sender_wallet_amount = 0
            currency_index = None

            for i in range(len(currency_wallet_id)):
                if wallet_id == currency_wallet_id[i] and transaction_currency == currency_type_list[i]:
                    sender_wallet_amount = balance[i]
                    currency_index = i

            # Check if the sender has the selected currency
            if sender_wallet_amount == 0:
                return JsonResponse({'status': 'currency_error', 'message': 'User does not have the selected currency'})

            # Check if the sender has enough funds for the transaction
            if transaction_amount > float(sender_wallet_amount):
                return JsonResponse({'status': 'insufficient_funds', 'message': 'Insufficient funds in wallet'})

            # If validation passes
            return JsonResponse({'status': 'success', 'message': 'Validation successful'})

        except Exception as e:
            return Response({'error': 'An unexpected error occurred', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class QRViewSet(viewsets.ModelViewSet):
    queryset = TransactionTable.objects.all()
    serializer_class = TransactionSerializer

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')  # Fetch user_id from frontend

        # Fetch the corresponding wallet details for the given user_id
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM fiat_wallet WHERE user_id = %s", [user_id])
            user_wallet = cursor.fetchone()  # Get the row for the given user_id

        if not user_wallet:
            return JsonResponse({'status': 'failure', 'message': 'Invalid User ID'})

        wallet_id = user_wallet[0]  # Get wallet_id from the user_wallet
        sender_mobile_number = user_wallet[7]  # Get mobile number

        # Fetch currency details
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

        # Fetch receiver details from fiat_wallet
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM fiat_wallet")
            rows = cursor.fetchall()

        receiver_numbers = [row[7] for row in rows]
        wallet_ids = [row[0] for row in rows]

        if request.data['user_phone_number'] not in receiver_numbers:
            return JsonResponse({'status': 'mobile_failure', 'message': 'Mobile Number Failure'})

        index = receiver_numbers.index(request.data['user_phone_number'])
        receiver_wallet_id = wallet_ids[index]

        user_currency_id_list = []
        sender_wallet_amount = []
        receiver_wallet_amount = []
        validation_list = []

        for i in range(len(currency_wallet_id)):
            if receiver_wallet_id == currency_wallet_id[i] and request.data.get('transaction_currency') == currency_type_list[i]:
                user_currency_id_list.append(currency_type_list[i])
                receiver_wallet_amount.append(balance[i])
            
            if wallet_id == currency_wallet_id[i] and request.data.get('transaction_currency') == currency_type_list[i]:
                validation_list.append(currency_type_list[i])
                sender_wallet_amount.append(balance[i])

        if len(validation_list) == 0:
            return JsonResponse({'status': 'currency_error', 'message': 'Payment Failure'})

        if float(request.data.get('transaction_amount')) <= float(sender_wallet_amount[0]) and len(user_currency_id_list) >= 1:
            deducted_amount = float(sender_wallet_amount[0]) - float(request.data.get('transaction_amount'))
            credit_amount = float(receiver_wallet_amount[0]) + float(request.data.get('transaction_amount'))

            # Update sender's and receiver's balances
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE user_currencies SET balance = %s WHERE wallet_id = %s AND currency_type = %s",
                    [deducted_amount, wallet_id, request.data.get('transaction_currency')]
                )
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE user_currencies SET balance = %s WHERE wallet_id = %s AND currency_type = %s",
                    [credit_amount, receiver_wallet_id, request.data.get('transaction_currency')]
                )

            request.data['wallet_id'] = wallet_id 
            return super().create(request, *args, **kwargs)

        elif float(request.data.get('transaction_amount')) <= float(sender_wallet_amount[0]) and len(user_currency_id_list) < 1:
            deducted_amount = float(sender_wallet_amount[0]) - float(request.data.get('transaction_amount'))
            credit_amount = float(request.data.get('transaction_amount'))

            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE user_currencies SET balance = %s WHERE wallet_id = %s AND currency_type = %s",
                    [deducted_amount, wallet_id, request.data.get('transaction_currency')]
                )
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO user_currencies (wallet_id, currency_type, balance)
                    VALUES (%s, %s, %s)
                    """,
                    [receiver_wallet_id, request.data.get('transaction_currency'), credit_amount]
                )

            return super().create(request, *args, **kwargs)

        else:
            return JsonResponse({'status': 'insufficient_funds', 'message': 'Payment Failure'})










class FiatAddressViewSet(viewsets.ModelViewSet):
    queryset = TransactionTable.objects.all()
    serializer_class = TransactionSerializer

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        fiat_address = request.data.get('fiat_address')
        transaction_amount = float(request.data.get('transaction_amount'))
        transaction_currency = request.data.get('transaction_currency')

        # Fetch wallet info based on fiat address
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM fiat_wallet WHERE fiat_wallet_address = %s", [fiat_address])
            fiat_wallet = cursor.fetchone()

        if not fiat_wallet:
            return JsonResponse({'status': 'address_failure', 'message': 'Fiat Address does not exist.'})

        try:
            # Fetch wallet ID based on user_id
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT fiat_wallet_id FROM fiat_wallet WHERE user_id = %s",
                    [user_id]
                )
                user_wallet = cursor.fetchone()

            if not user_wallet:
                return JsonResponse({'status': 'failure', 'message': 'No wallet record found for the given user ID.'})

            user_wallet_id = user_wallet[0]  # Wallet ID is in the first column

            # Check if the selected currency exists in the user_currencies table for the user's wallet ID
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT balance FROM user_currencies WHERE wallet_id = %s AND currency_type = %s",
                    [user_wallet_id, transaction_currency]
                )
                currency_balance = cursor.fetchone()

            if not currency_balance:
                return JsonResponse({'status': 'currency_failure', 'message': 'Selected currency not found in the wallet.'})

            current_balance = float(currency_balance[0])

            # Validate if transaction amount is less than or equal to the current balance
            if transaction_amount > current_balance:
                return JsonResponse({'status': 'failure', 'message': 'Insufficient funds in the selected currency.'})

            # Deduct the transaction amount from the selected currency balance
            updated_balance = current_balance - transaction_amount
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE user_currencies SET balance = %s WHERE wallet_id = %s AND currency_type = %s",
                    [updated_balance, user_wallet_id, transaction_currency]
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

            request.data['wallet_id'] = user_wallet_id

            # Proceed with creating the transaction record
            return super().create(request, *args, **kwargs)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class TransactionValidationViewSet(viewsets.ViewSet):
    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        fiat_address = request.data.get('fiat_address')
        transaction_amount = float(request.data.get('transaction_amount'))
        transaction_currency = request.data.get('transaction_currency')

        # Fetch wallet info based on fiat address
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM fiat_wallet WHERE fiat_wallet_address = %s", [fiat_address])
            fiat_wallet = cursor.fetchone()

        if not fiat_wallet:
            return Response({'status': 'address_failure', 'message': 'Fiat Address does not exist.'})

        try:
            # Fetch wallet ID based on user_id
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT fiat_wallet_id FROM fiat_wallet WHERE user_id = %s",
                    [user_id]
                )
                user_wallet = cursor.fetchone()

            if not user_wallet:
                return Response({'status': 'failure', 'message': 'No wallet record found for the given user ID.'})

            user_wallet_id = user_wallet[0]  # Wallet ID is in the first column

            # Check if the selected currency exists in the user_currencies table for the user's wallet ID
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT balance FROM user_currencies WHERE wallet_id = %s AND currency_type = %s",
                    [user_wallet_id, transaction_currency]
                )
                currency_balance = cursor.fetchone()

            if not currency_balance:
                return Response({'status': 'currency_failure', 'message': 'Selected currency not found in the wallet.'})

            current_balance = float(currency_balance[0])

            # Validate if transaction amount is less than or equal to the current balance
            if transaction_amount > current_balance:
                return Response({'status': 'failure', 'message': 'Insufficient funds in the selected currency.'})

            return Response({'status': 'success', 'message': 'Validation successful.'})

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





