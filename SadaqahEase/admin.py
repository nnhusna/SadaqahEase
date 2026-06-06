from django.contrib import admin
from .models import Donor,Admin,Treasurer,Campaign,Donation,Financial,Report,TabungDonation,AllocateFund

# Register your models here.

admin.site.register(Donor)
admin.site.register(Admin)
admin.site.register(Treasurer)
admin.site.register(Campaign)
admin.site.register(Donation)
admin.site.register(Financial)
admin.site.register(Report)
admin.site.register(TabungDonation)
admin.site.register(AllocateFund)

