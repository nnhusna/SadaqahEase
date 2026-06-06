from django.db import models
from django.core.files import File
import uuid
from datetime import date
from django.utils import timezone

# Create your models here.

# ---------------------- Donor ----------------------
class Donor(models.Model):
    donorid = models.CharField(max_length=8, primary_key=True, editable=False)
    fullname = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    dob = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.donorid:
            self.donorid = 'DN' + uuid.uuid4().hex[:6].upper()
        super(Donor, self).save(*args, **kwargs)

    def __str__(self):
        return self.fullname

# ---------------------- Admin ----------------------
class Admin(models.Model):
    adminid = models.CharField(max_length=6, primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# ---------------------- Treasurer ----------------------
class Treasurer(models.Model):
    treasurerid = models.CharField(max_length=6, primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# ---------------------- Campaign ----------------------
class Campaign(models.Model):
    campaignid = models.CharField(max_length=6, primary_key=True)
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=2000)
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    campaignimage = models.ImageField(upload_to='campaign_images/', null=True, blank=True)

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def percentage(self):
        if self.goal_amount:
            return round((self.current_amount / self.goal_amount) * 100, 2)
        return 0

    def days_left(self):
        return max((self.end_date - date.today()).days, 0)

    def is_ongoing(self):
        return self.status == 'Approved' and self.start_date <= date.today() <= self.end_date

    def is_completed(self):
        return self.status == 'Approved' and self.end_date < date.today()

    def __str__(self):
        return self.title


# ---------------------- Donation ----------------------
class Donation(models.Model):
    DONATION_TYPE_CHOICES = [
        ('General', 'General Donation'),
        ('Campaign', 'Campaign Donation'),
    ]

    donationid = models.CharField(max_length=10, primary_key=True, editable=False)
    donorid = models.ForeignKey('Donor', on_delete=models.SET_NULL, null=True, blank=True)
    campaignid = models.ForeignKey('Campaign', on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_donated = models.DateField()
    receipt = models.ImageField(upload_to='donation_receipts/', null=True, blank=True)
    donation_type = models.CharField(max_length=10, choices=DONATION_TYPE_CHOICES, default='General')
    hidden_from_donor = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.donationid:
            unique_id = uuid.uuid4().hex[:6].upper()
            self.donationid = f'DN{unique_id}'
        super().save(*args, **kwargs)
    def campaign_display_id(self):
            return "GENERAL" if not self.campaignid else self.campaignid.campaignid

    def __str__(self):
        return f"{self.get_donation_type_display()} - RM{self.amount} to {self.campaign_display_id()} on {self.date_donated}"

# ---------------------- Financial ----------------------
class Financial(models.Model):
    FINANCIAL_TYPE_CHOICES = [
        ('Income', 'Income'),
        ('Expense', 'Expense'),
    ]

    SOURCE_CHOICES = [
        ('Online Donation', 'Online Donation'),
        ('Tabung (Physical Box)', 'Tabung (Physical Box)'),
        ('Campaign', 'Campaign'),
        ('Others', 'Others'),
    ]

    PURPOSE_CHOICES = [
        ('Asnaf Support', 'Asnaf Support'),
        ('Mosque Maintenance', 'Mosque Maintenance'),
        ('Utilities', 'Utilities'),
        ('Education Program', 'Education Program'),
        ('Community Event', 'Community Event'),
        ('Others', 'Others'),
    ]

    financialid = models.AutoField(primary_key=True)
    date = models.DateField()
    type = models.CharField(max_length=10, choices=FINANCIAL_TYPE_CHOICES)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, blank=True, null=True)  # for Income
    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES, blank=True, null=True)  # for Expense
    description = models.TextField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    recorded_by = models.ForeignKey(Treasurer, on_delete=models.SET_NULL, null=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return f"{self.type} - RM{self.amount} on {self.date}"

# ---------------------- Report ----------------------
class Report(models.Model):
    reportid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    generated_date = models.DateTimeField(auto_now_add=True)
    total_donations = models.DecimalField(max_digits=12, decimal_places=2)
    generated_by = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to='reports/')

    def __str__(self):
        return self.title
    
class TabungDonation(models.Model):
    donationid = models.CharField(primary_key=True, max_length=10, editable=False)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.donationid:
            unique_id = uuid.uuid4().hex[:6].upper()
            self.donationid = f'TB{unique_id}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Tabung - RM{self.amount} on {self.date}"
    
class AllocateFund(models.Model):
    CATEGORY_CHOICES = [
        ('Education Program', 'Education Program'),
        ('Mosque Maintenance', 'Mosque Maintenance'),
        ('Asnaf Support', 'Asnaf Support'),
        ('Utilities', 'Utilities'),
        ('Community Event', 'Community Event'),
        ('Others', 'Others'),
    ]

    allocateid = models.AutoField(primary_key=True)
    date = models.DateField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(max_length=200)
    recorded_by = models.ForeignKey(Treasurer, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.category} - RM{self.amount} on {self.date}"