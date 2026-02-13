from django.db import models
from django.utils import timezone


class CustomUser(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone =  models.CharField(max_length=15)
    password = models.CharField(max_length=128)
    image = models.ImageField(
        upload_to='userImage',
        default='userImage/default.png',
        blank=True,
        null=True
    )
    address = models.CharField(max_length=100, blank=True, null=True)
    reg_date = models.DateTimeField(auto_now_add=True)
    as_user = models.BooleanField(default=False)
    as_host = models.BooleanField(default=False)

    def __str__(self):
        role = "Host" if self.as_host else "User"
        return f"{self.first_name} {self.last_name} ({role})"

class CategoryOfServices(models.Model):
    services_name = models.CharField(max_length=50)
    servise_provider_mail = models.EmailField()
    reg_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.services_name

class OfferOfListingProperty(models.Model):
    offerPercentage = models.DecimalField(max_digits=5, decimal_places=2)  # e.g. 10.50 %
    offer_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.offerPercentage}% Offer"
    
class HostProfile(models.Model):  # one-to-one relation with CustomUser
    host = models.OneToOneField( CustomUser, on_delete=models.CASCADE, related_name="host_profile")
    bio = models.TextField(blank=True, null=True)
    profile_photo = models.ImageField(upload_to='hostImage/',default='hostImage/default_host.png', blank=True, null=True)
    govt_id_type = models.CharField(
        max_length=50,
        choices=[
            ('aadhaar', 'Aadhaar Card'),
            ('passport', 'Passport'),
            ('driving_license', 'Driving License'),
            ('pan', 'PAN Card')
        ],blank=True,null=True)
    govt_id_number = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    verified_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"HostProfile of {self.host.first_name}"
    class Meta:
        verbose_name = "Host Profile"
        verbose_name_plural = "Host Profiles"

class ListingProperty(models.Model):
    host = models.ForeignKey(HostProfile, on_delete=models.CASCADE, related_name="properties")
    category = models.ForeignKey(CategoryOfServices, on_delete=models.SET_NULL, null=True, blank=True)
    offer = models.ForeignKey(OfferOfListingProperty, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    pincode = models.CharField(max_length=40)
    guests_allowed = models.IntegerField(default=1)
    bedrooms = models.IntegerField(default=1)
    bathrooms = models.IntegerField(default=1)
    beds = models.IntegerField(default=1)
       
    # Facilities
    wifi = models.BooleanField(default=False)
    pools = models.BooleanField(default=False)
    gym = models.BooleanField(default=False)
    pickupFacility = models.BooleanField(default=False)
    smoking = models.BooleanField(default=False)
    food = models.BooleanField(default=False)
    parking = models.BooleanField(default=False)
    securityCam = models.BooleanField(default=False)
    tv = models.BooleanField(default=False)
    Ac = models.BooleanField(default=False)
    filterWater = models.BooleanField(default=False)
    StayLongAllow = models.BooleanField(default=False)
    

    is_available = models.BooleanField(default=True)
    available_from = models.DateField(blank=True, null=True)
    available_to = models.DateField(blank=True, null=True)
    reg_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.host}  - - - -  {self.title}"


class PropertyImage(models.Model):
    Owner = models.EmailField()
    property = models.ForeignKey(ListingProperty, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="propertyImages")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image of {self.property.title}"








class AddToWishList(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE, related_name='wishlist')
    property = models.ForeignKey(ListingProperty,on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'property') 
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.first_name} added {self.property.title} to wishlist"
    
        



class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    property = models.ForeignKey(ListingProperty, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.IntegerField(default=1)
    nights = models.IntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'property') 

    def __str__(self):
        return f"Booking #{self.id} by ---- {self.user.first_name} --- for --- {self.property.title} --- of Host --- {self.property.host.host.first_name} --- {self.status}"


    
class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    razorpay_order_id = models.CharField(max_length=100)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")
    captured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for booking {self.booking.id} - {self.amount} {self.currency}"





class HostLoginDetailsHistory(models.Model):
    host = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    last_names = models.CharField(max_length=50)
    image = models.ImageField(upload_to="host_image_login", blank=True, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    login_time = models.DateTimeField(default=timezone.now)
    login_count = models.IntegerField(default=1)
    status_login = models.BooleanField(default=False)

    def __str__(self):
        return f"Login history for {self.host.email} at {self.login_time}"



class AdminAllMutedFiledSwich(models.Model):
    muteAddProperty = models.BooleanField(False)
    muteAddServices = models.BooleanField(False)
    muteEdit = models.BooleanField(False)
    muteNotifications = models.BooleanField(False)
    muteNotificationManageMent = models.BooleanField(False)



 

class UserFeedback(models.Model):
    host = models.ForeignKey(HostProfile,on_delete=models.CASCADE,related_name="feedbacks")
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="feedbacks")
    property = models.ForeignKey(ListingProperty,on_delete=models.CASCADE,related_name="feedbacks")
    host_name = models.CharField(max_length=50)
    message = models.CharField(max_length=400)
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Feedback by {self.user} for {self.host}"        
    





class UserReportSectionOfHost(models.Model):
        host = models.ForeignKey(HostProfile, on_delete=models.CASCADE)
        user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
        report_count = models.IntegerField(default=1)
        reason = models.TextField(blank=True, null=True)
        is_resolved = models.BooleanField(default=False)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        class Meta:
            unique_together = ('host', 'user')

        def __str__(self):
            return f"{self.user} reported {self.host}"


        








from django.db import models
from django.utils import timezone
from .models import Booking, Payment, CustomUser

class Refund(models.Model):
    REFUND_STATUS = [
        ("requested", "Requested"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("completed", "Completed"),
    ]
    
    REFUND_METHOD = [
        ("system", "System Payment"),
        ("bank", "Bank Transfer"),
        ("upi", "UPI Transfer"),
        ("manual", "Manual Transfer"),
    ]

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="refund"
    )
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="refunds",
        null=True,
        blank=True
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    refund_method = models.CharField(max_length=20, choices=REFUND_METHOD, default="system")
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=REFUND_STATUS,
        default="requested"
    )
    admin_comment = models.TextField(blank=True, null=True)
    
    # Transaction details
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    bank_account = models.CharField(max_length=100, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    upi_id = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    refund_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Refund #{self.id} - Booking {self.booking.id}"

    def save(self, *args, **kwargs):
        if self.status == "completed" and not self.refund_date:
            self.refund_date = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']












class PaymentsForHostByAdmin(models.Model):

    PAYMENT_STATUS = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("on_hold", "On Hold"),
    ]

    host = models.ForeignKey(HostProfile,on_delete=models.CASCADE,related_name="monthly_payments")

    month = models.IntegerField()   # 1 - 12
    year = models.IntegerField()

    total_properties = models.IntegerField(default=0)
    commission_per_property = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    penalty = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    final_payout = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20,choices=PAYMENT_STATUS,default="pending")

    remarks = models.TextField(blank=True, null=True)
    generated_at = models.DateTimeField(default=timezone.now)
    paid_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('host', 'month', 'year')
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.host.host.email} - {self.month}/{self.year}"

    




