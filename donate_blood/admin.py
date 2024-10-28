from django.contrib import admin

from .models import UserAccount, DonationRequest, DonatioHistory, DonationAccepted, ContactForm, Payment
# Register your models here.
admin.site.register(UserAccount),
admin.site.register(DonationRequest),
admin.site.register(DonatioHistory),
admin.site.register(DonationAccepted),
admin.site.register(ContactForm),
admin.site.register(Payment),