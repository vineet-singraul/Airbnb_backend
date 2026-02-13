from rest_framework import serializers
from .models import CategoryOfServices,HostProfile,ListingProperty,AddToWishList



# serializers.py

from rest_framework import serializers
from .models import CustomUser, UserFeedback, HostProfile


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'phone',
            'image',
            'address',
            'as_user',
            'as_host',
            'reg_date',
        ]
        read_only_fields = ['id', 'reg_date']



# ======== Host Ne Jitni Catagureis Add Ki Hai Utni Show Karna  ============
class ServicesSerializers(serializers.ModelSerializer):
    class Meta:
        model = CategoryOfServices
        fields = ['id','services_name','servise_provider_mail','reg_date']

# ========= Host Ke Profile Ka Serializer Hai Ye ======================
class HostProfileSerializer(serializers.ModelSerializer):
    host_name = serializers.CharField(source='host.first_name', read_only=True)
    last_name = serializers.CharField(source='host.last_name', read_only=True)
    email = serializers.EmailField(source='host.email', read_only=True)
    phone = serializers.CharField(source='host.phone', read_only=True)
    image = serializers.ImageField(source='host.image', read_only=True)
    user_address = serializers.CharField(source='host.address', read_only=True)
    as_host = serializers.BooleanField(source='host.as_host', read_only=True)

    class Meta:
        model = HostProfile
        fields = [
            'id',
            'host_name',
            'last_name',
            'email',
            'phone',
            'image',
            'user_address',
            'as_host',
            'bio',
            'profile_photo',
            'govt_id_type',
            'govt_id_number',
            'address',        # HostProfile address
            'city',
            'country',
            'verified_status',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
        


# ========= Listing Property Serializer ======================
class ListingPropertySerializer(serializers.ModelSerializer):
    host_name = serializers.CharField(source='host.host.first_name', read_only=True)
    host_email = serializers.EmailField(source='host.host.email', read_only=True)
    phone = serializers.CharField(source='host.host.phone', read_only=True)  # ✅ Correct source added
    category_name = serializers.CharField(source='category.services_name', read_only=True)
    offer_percentage = serializers.DecimalField(source='offer.offerPercentage', max_digits=5, decimal_places=2, read_only=True)

    images = serializers.SerializerMethodField()

    class Meta:
        model = ListingProperty
        fields = [
            'id', 'host_name', 'host_email', 'phone',
            'category', 'category_name', 'offer', 'offer_percentage',
            'title', 'description', 'price_per_night', 'location', 'city', 'country', 'pincode',
            'guests_allowed', 'bedrooms', 'bathrooms', 'beds',
            'wifi', 'pools', 'gym', 'pickupFacility', 'smoking', 'food',
            'parking', 'securityCam', 'tv', 'Ac', 'filterWater', 'StayLongAllow',
            'is_available', 'available_from', 'available_to', 'reg_date', 'images',
        ]
        read_only_fields = [
            'id', 'host_name', 'host_email', 'category_name',
            'offer_percentage', 'reg_date', 'images', 'phone'
        ]

    def get_images(self, obj):
        request = self.context.get('request')
        return [
            request.build_absolute_uri(image.image.url)
            for image in obj.images.all()
        ]

# ========= Property With Images Serializer ======================
class PropertyWithImagesSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    host = serializers.SerializerMethodField()

    class Meta:
        model = ListingProperty
        fields = [
            'id', 'title', 'description', 'price_per_night',
            'location', 'city', 'country', 'pincode',
            'guests_allowed', 'bedrooms', 'bathrooms', 'beds',
            'wifi', 'pools', 'gym', 'pickupFacility', 'smoking', 'food',
            'parking', 'securityCam', 'tv', 'Ac', 'filterWater', 'StayLongAllow',
            'is_available', 'available_from', 'available_to', 'reg_date',
            'images', 'host'
        ]

    def _get_property_extras(self, obj):
        request = self.context.get('request')

        # --- Get images ---
        images = []
        if hasattr(obj, 'images'):
            images = [
                request.build_absolute_uri(img.image.url)
                for img in obj.images.all()
            ]

        # --- Get host info ---
        host_profile = getattr(obj, 'host', None)
        host_data = None
        if host_profile:
            host_data = {
                "id": host_profile.id,
                "host_name": host_profile.host.first_name,
                "email": host_profile.host.email,
                "phone": getattr(host_profile.host, 'phone', None),  # ✅ added phone safely
                "bio": host_profile.bio,
                "profile_photo": (
                    request.build_absolute_uri(host_profile.profile_photo.url)
                    if host_profile.profile_photo else None
                ),
                "govt_id_type": host_profile.govt_id_type,
                "govt_id_number": host_profile.govt_id_number,
                "address": host_profile.address,
                "city": host_profile.city,
                "country": host_profile.country,
                "verified_status": host_profile.verified_status,
                "created_at": host_profile.created_at,
            }

        return images, host_data

    def get_images(self, obj):
        images, _ = self._get_property_extras(obj)
        return images

    def get_host(self, obj):
        _, host = self._get_property_extras(obj)
        return host











class WishListSerializer(serializers.ModelSerializer):
    property = PropertyWithImagesSerializer(read_only=True)

    class Meta:
        model = AddToWishList
        fields = [
            'id',
            'user',
            'property',
            'added_at',
        ]
        read_only_fields = ['id', 'user', 'property', 'added_at']







from rest_framework import serializers
from .models import Booking, Payment
from .models import ListingProperty, CustomUser


class BookingSerializer(serializers.ModelSerializer):
    property = PropertyWithImagesSerializer(read_only=True)
    user = serializers.SerializerMethodField()   
    class Meta:
        model = Booking
        fields = '__all__'

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "email": obj.user.email,
            "phone": getattr(obj.user, "phone", None),
        }
  



        

class CreateOrderSerializer(serializers.Serializer):
    property_id = serializers.IntegerField()
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    guests = serializers.IntegerField()
    # client user id - this example assumes you pass user id (or use auth)
    user_id = serializers.IntegerField()





from rest_framework import serializers
from .models import HostLoginDetailsHistory
from .models import CustomUser


class HostLoginDetailsHistorySerializer(serializers.ModelSerializer):
    host_email = serializers.EmailField(source='host.email', read_only=True)
    host_id = serializers.IntegerField(source='host.id', read_only=True)

    class Meta:
        model = HostLoginDetailsHistory
        fields = [
            'id',
            'host_id',
            'host_email',
            'name',
            'last_names',
            'image',
            'lat',
            'lon',
            'city',
            'state',
            'country',
            'login_time',
            'login_count',
            'status_login'
        ]
        read_only_fields = ['login_time', 'login_count']








from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):

    user_details = serializers.SerializerMethodField()
    host_details = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id',
            'razorpay_order_id',
            'razorpay_payment_id',
            'amount',
            'currency',
            'captured',
            'created_at',
            'user_details',
            'host_details',
        ]

    # ---------- User ----------
    def get_user_details(self, obj):
        user = obj.booking.user
        request = self.context.get('request')

        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
            "image": (
                request.build_absolute_uri(user.image.url)
                if request and user.image else None
            ),
            "address": user.address,
        }

    # ---------- Host ----------
    def get_host_details(self, obj):
        host_profile = obj.booking.property.host
        host = host_profile.host
        request = self.context.get('request')

        return {
            "host_profile_id": host_profile.id,
            "host_id": host.id,
            "first_name": host.first_name,
            "last_name": host.last_name,
            "email": host.email,
            "phone": host.phone,
            "profile_photo": (
                request.build_absolute_uri(host_profile.profile_photo.url)
                if request and host_profile.profile_photo else None
            ),
            "city": host_profile.city,
            "country": host_profile.country,
            "verified_status": host_profile.verified_status,
        }
    







from .models import AdminAllMutedFiledSwich

class AdminAllMutedFiledSwichSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminAllMutedFiledSwich
        fields = [
            "id",
            "muteAddProperty",
            "muteAddServices",
            "muteEdit",
            "muteNotifications",
            "muteNotificationManageMent",
        ]






class UserFeedbackSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    host = HostProfileSerializer(read_only=True)

    class Meta:
        model = UserFeedback
        fields = [
            'id',
            'host_name',
            'message',
            'phone',
            'created_at',
            'user',
            'host',
            'property',
        ]
        read_only_fields = ['id', 'created_at']






from rest_framework import serializers
from .models import UserReportSectionOfHost, CustomUser, HostProfile

# --- Simple User Serializer for nested display ---
class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'email', 'phone']

# --- Main Serializer ---
class UserReportSectionOfHostSerializer(serializers.ModelSerializer):

    # READ ke liye nested data
    user = SimpleUserSerializer(read_only=True)
    host = HostProfileSerializer(read_only=True)

    # WRITE ke liye (POST me IDs)
    user_id = serializers.IntegerField(write_only=True)
    host_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = UserReportSectionOfHost
        fields = [
            'id',
            'user',
            'host',
            'user_id',
            'host_id',
            'report_count',
            'reason',
            'is_resolved',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'report_count',
            'is_resolved',
            'created_at',
            'updated_at',
        ]

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        host_id = validated_data.pop('host_id')

        # Get User and Host objects
        user = CustomUser.objects.get(id=user_id)
        host = HostProfile.objects.get(id=host_id)

        reason = validated_data.get('reason', '')

        # Check if report already exists
        report, created = UserReportSectionOfHost.objects.get_or_create(
            user=user,
            host=host,
            defaults={'reason': reason}
        )

        # Agar report already exist karti hai → increment report_count
        if not created:
            report.report_count += 1
            if reason:
                report.reason = reason
            report.save() 

        return report








from rest_framework import serializers
from .models import Refund

class RefundSerializer(serializers.ModelSerializer):
    booking_id = serializers.IntegerField(source="booking.id", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Refund
        fields = "__all__"




from rest_framework import serializers
from .models import PaymentsForHostByAdmin


class AdminHostSalarySerializer(serializers.ModelSerializer):
    host = serializers.SerializerMethodField()

    class Meta:
        model = PaymentsForHostByAdmin
        fields = [
            "id",
            "host",
            "month",
            "year",
            "total_properties",
            "commission_per_property",
            "total_commission",
            "bonus",
            "penalty",
            "final_payout",
            "status",
            "remarks",
            "generated_at",
            "paid_at",
        ]

    def get_host(self, obj):
        user = obj.host.host 
        return {
            "id": obj.host.id,
            "name": f"{user.first_name} {user.last_name}",
            "email": user.email,
            "phone": user.phone,
        }























