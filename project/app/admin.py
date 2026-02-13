from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(CategoryOfServices)
admin.site.register(OfferOfListingProperty)
admin.site.register(ListingProperty)
admin.site.register(PropertyImage)
admin.site.register(HostProfile)
admin.site.register(Booking)  
admin.site.register(Payment) 
admin.site.register(UserFeedback)  
admin.site.register(PaymentsForHostByAdmin)