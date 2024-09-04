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
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # Higher error correction
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        # Customizing the colors
        img = qr.make_image(fill_color="black", back_color="lightgrey")

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
    transaction_type = models.CharField(max_length=50 ,null=True, blank=True)
    transaction_amount = models.DecimalField(max_digits=18, decimal_places=8 ,null=True, blank=True)
    transaction_currency = models.CharField(max_length=10 ,null=True, blank=True)
    transaction_timestamp = models.DateTimeField(auto_now_add=True)
    transaction_status = models.CharField(max_length=50 ,null=True, blank=True)
    transaction_hash = models.CharField(max_length=255, unique=True)
    transaction_fee = models.DecimalField(max_digits=18, decimal_places=8, null=True, blank=True)
    user_phone_number = models.CharField(max_length=15 , null=True, blank=True)
    wallet_id = models.CharField(max_length=100 ,null=True, blank=True)
    sender_mobile_number= models.CharField(max_length=15 ,null=True, blank=True)
    fiat_address = models.CharField(max_length=255, null=True, blank=True)
    transaction_method = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'transaction_table'
        managed: False

    def __str__(self):
        return f"{self.transaction_id} - {self.transaction_amount} {self.transaction_currency}"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()


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
    

    def sender_mobile_number_fetch(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM currency_converter_fiatwallet")
            rows = cursor.fetchall()
        print(rows[-1][7])
        return rows[-1][7]

