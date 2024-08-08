from django.db import models
import re

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

    class Meta:
        db_table = 'transaction_table'

    def __str__(self):
        return f"{self.transaction_id} - {self.transaction_amount} {self.transaction_currency}"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()

        super().save(*args, **kwargs)

    def generate_transaction_id(self):
        latest_transaction = TransactionTable.objects.order_by('-transaction_id').first()
        if latest_transaction and re.search(r'\d+', latest_transaction.transaction_id):
            last_id = latest_transaction.transaction_id
            number = int(re.search(r'\d+', last_id).group())
            new_number = number + 1
            return f'TRANS{new_number:06d}'
        return 'TRANS000001'
