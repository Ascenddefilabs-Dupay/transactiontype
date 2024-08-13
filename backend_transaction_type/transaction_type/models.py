from django.db import models
import re
import hashlib
import uuid
from django.db import connection
import qrcode
from io import BytesIO
import base64


class User(models.Model):
    name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    qr_code = models.TextField(blank=True, null=True)

    def generate_qr_code(self):
        qr_data = f"{self.name}-{self.mobile_number}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        self.qr_code = img_str
        self.save()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'registration'





# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class TransactionTable(models.Model):
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, editable=False, primary_key=True)
    transaction_type = models.CharField(max_length=50)
    transaction_amount = models.DecimalField(max_digits=18, decimal_places=8)
    transaction_currency = models.CharField(max_length=10)
    transaction_timestamp = models.DateTimeField(auto_now_add=True)
    transaction_status = models.CharField(max_length=50)
    transaction_hash = models.CharField(max_length=255, unique=True)
    transaction_fee = models.DecimalField(max_digits=18, decimal_places=8, null=True, blank=True)
    person_phone_number = models.CharField(max_length=15)
    wallet_id = models.CharField(max_length=100)
    sender_mobile_number= models.CharField(max_length=15)

    class Meta:
        db_table = 'transaction_table'

    def __str__(self):
        return f"{self.transaction_id} - {self.transaction_amount} {self.transaction_currency}"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()

        if not self.wallet_id:
            self.wallet_id = self.wallet_id_fetch()

        if not self.sender_mobile_number:
            self.sender_mobile_number = self.sender_mobile_number_fetch()
        

        super().save(*args, **kwargs)

    def generate_transaction_id(self):
        latest_transaction = TransactionTable.objects.order_by('-transaction_id').first()
        if latest_transaction and re.search(r'\d+', latest_transaction.transaction_id):
            last_id = latest_transaction.transaction_id
            number = int(re.search(r'\d+', last_id).group())
            new_number = number + 1
            return f'TRANS{new_number:06d}'
        return 'TRANS000001'
    
    def wallet_id_fetch(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM wallet_table")
            rows = cursor.fetchall()
        print(rows[-1][1])
        return rows[-1][1]
    def sender_mobile_number_fetch(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM wallet_table")
            rows = cursor.fetchall()
        print(rows[-1][2])
        return rows[-1][2]


class WalletTable(models.Model):
    wallet_id = models.CharField(max_length=100, unique=True, blank=True, editable=False, primary_key=True)
    mobile_number = models.CharField(max_length=15, unique=True)

    class Meta:
        db_table = 'wallet_table'

    def __str__(self):
        return f"{self.wallet_id} - {self.mobile_number}"

    def save(self, *args, **kwargs):
        if not self.wallet_id:
            self.wallet_id = self.generate_wallet_id()
        super().save(*args, **kwargs)

    def generate_wallet_id(self):
        latest_wallet = WalletTable.objects.order_by('-wallet_id').first()
        if latest_wallet and re.search(r'\d+', latest_wallet.wallet_id):
            last_id = latest_wallet.wallet_id
            number = int(re.search(r'\d+', last_id).group())
            new_number = number + 1
            return f'WALLET{new_number:06d}'
        return 'WALLET000001'
    


class Address(models.Model):
    wallet_id = models.CharField(max_length=100, unique=True)
    mobile_number = models.CharField(max_length=15)
    fiat_address = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'address'

    def __str__(self):
        return f"{self.wallet_id} - {self.mobile_number}"
    

class AddressBasedTransaction(models.Model):
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, editable=False, primary_key=True)
    transaction_type = models.CharField(max_length=50)
    transaction_amount = models.DecimalField(max_digits=18, decimal_places=8)
    transaction_currency = models.CharField(max_length=10)
    transaction_timestamp = models.DateTimeField(auto_now_add=True)
    transaction_status = models.CharField(max_length=50)
    transaction_hash = models.CharField(max_length=255, unique=True, blank=True, editable=False)
    fiat_address = models.CharField(max_length=255)

    class Meta:
        db_table = 'address_based_transaction'

    def __str__(self):
        return f"{self.transaction_id} - {self.transaction_amount} {self.transaction_currency}"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()

        if not self.transaction_hash:
            self.transaction_hash = self.generate_transaction_hash()

        super().save(*args, **kwargs)

    def generate_transaction_id(self):
        latest_transaction = AddressBasedTransaction.objects.order_by('-transaction_id').first()
        if latest_transaction and re.search(r'\d+', latest_transaction.transaction_id):
            last_id = latest_transaction.transaction_id
            number = int(re.search(r'\d+', last_id).group())
            new_number = number + 1
            return f'TRANS{new_number:06d}'
        return 'TRANS000001'

    def generate_transaction_hash(self):
        unique_string = f"{self.transaction_id}{self.transaction_amount}{self.transaction_timestamp}{uuid.uuid4()}"
        return hashlib.sha256(unique_string.encode()).hexdigest()