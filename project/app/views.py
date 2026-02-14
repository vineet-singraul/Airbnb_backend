from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import *
from django.contrib.auth import authenticate
from rest_framework import status

import os
import razorpay
from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .models import ListingProperty, CustomUser, Booking, Payment
from .serializers import BookingSerializer, CreateOrderSerializer
from django.views.decorators.csrf import csrf_exempt
import hmac
import hashlib
import json
from django.db.models import F


@api_view(['POST'])
def host_login_api(request):
    userEmail = request.data.get('userEmail')
    userPassword = request.data.get('userPassword')
    lat = request.data.get('lat')
    lon = request.data.get('lon')
    city = request.data.get('city')
    state = request.data.get('state')
    country = request.data.get('country')
    try:
        user = CustomUser.objects.get(email=userEmail, password=userPassword)

        if not user.as_host:
            return Response({"message": "Login As Host"}, status=401)

        # Save login history (multiple logins)
        history, created = HostLoginDetailsHistory.objects.get_or_create(
            host=user,
            defaults={
                "name": user.first_name,
                "last_names": user.last_name,
                "image": user.image,
                "lat": lat,
                "lon": lon,
                "city": city,
                "state": state,
                "country": country,
                "status_login": True
            }
        )

        if not created:
            # Existing record → update
            history.login_count += 1
            history.lat = lat
            history.lon = lon
            history.city = city
            history.state = state
            history.country = country
            history.status_login = True
            history.login_time = timezone.now()
            history.save()

        return Response({
            "message": "Login successful",
            "userEmail": userEmail,
            "lat": lat,
            "lon": lon,
            "city": city,
            "state": state,
            "country": country
        }, status=200)

    except CustomUser.DoesNotExist:
        return Response({"message": "Invalid Credentials"}, status=401)




@api_view(['POST'])
def host_addservices(request):
    addServicesName = request.data.get('addServicesName')
    hostname = request.data.get('hostname')
    
    try:
        host = CustomUser.objects.get(email=hostname)
    except CustomUser.DoesNotExist:
        return Response({"message":"Host Not Found"},status=401)
    
    CategoryOfServices.objects.create(
        services_name=addServicesName,
        servise_provider_mail=hostname
    )
    return Response({"message": "Service added successfully!"}, status=200)

from .serializers import ServicesSerializers
@api_view(['POST','GET'])
def host_manageServices(request):
        hostname = request.data.get('hostname')
        HostServicesDetails = CategoryOfServices.objects.filter(servise_provider_mail=hostname)
        serializer = ServicesSerializers(HostServicesDetails,many=True)
        try:
          return Response(serializer.data,status=200)
        except Exception as e:
          return Response({"error": str(e)}, status=500)
        
from .serializers import HostProfileSerializer
@api_view(['POST'])
def host_Profile(request):
    # =============== POST REQUEST ===============
        try:
            host_email = request.data.get('hostName') 
            host_detail = request.data.get('inputVal')
            address = request.data.get('address')

            host = CustomUser.objects.get(email=host_email)
            if isinstance(host_detail, dict):
                bio = host_detail.get('bio')
                govt_id_type = host_detail.get('documentName')
                govt_id_number = host_detail.get('documentNumber')
                city = host_detail.get('city')
                country = host_detail.get('country')
            else:
                bio = host_detail
                govt_id_type = govt_id_number = city = country = None

            host_profile = HostProfile.objects.create(
                host=host,
                bio=bio,
                govt_id_type=govt_id_type,
                govt_id_number=govt_id_number,
                address=address,
                city=city,
                country=country,
            )
            return Response(
                {
                    "message": "Host profile created successfully!",
                    "host_profile_id": host_profile.id,
                },
                status=status.HTTP_201_CREATED,
            )

        except CustomUser.DoesNotExist:
            return Response({"error": "Host not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print("❌ Error:", e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# =================== """" END HAER """""" ==========================

# ====== ** YAHA SE HOST KI ADD PROPERTY PAGE ME CATEGURIES JAYEGI ** ====== // 
@api_view(['GET'])
def ShowAll_Category_In_Select_Tag(request):
    try:
        host_email = request.query_params.get('email')
        if not host_email:
            return Response(status=401)
        allServices = CategoryOfServices.objects.filter(servise_provider_mail=host_email)
        if not allServices.exists():
            return Response(status=401)
        # Sari Categoryies Nikalana
        serializer = ServicesSerializers(allServices, many=True)  

        # Check Karna Ki Verfy Hai // OR // Nhi
        varify = HostProfile.objects.get(host__email=host_email)

        return Response({"data": serializer.data},status=200)
    except Exception as e:
        return Response({"error": f"Something went wrong: {str(e)}"},status=401)
# =================== """" END HAER """""" ==================================

# ====== ** YAHA SE CHECK HO RAHA KI HOST STATUS VERIFIED HAI KI NHI ** ====== // 
@api_view(['GET'])
def IsHostVarifeid(request):
    print("+++++++++ ---------------- +++++++++++++++++++")
    # =============== GET REQUEST ===============
    if request.method == 'GET':
        host_email = request.query_params.get('email')

        if not host_email:
            return Response({"error": "Email parameter is required"}, status=401)

        host_profiles = HostProfile.objects.filter(host__email=host_email)
        if not host_profiles.exists():
            return Response({"message": "No host profile found for this email"}, status=401)


        serializer = HostProfileSerializer(host_profiles, many=True, context={'request': request})
        hostId = serializer.data[0]['id']
        hostDat = HostProfile.objects.get(id=hostId)

        host_image = str(hostDat.host.image) if hostDat.host.image else None
        host_name = hostDat.host.first_name
        is_verified = getattr(hostDat, "is_verified", None)
        # 🟢 Combine all data in one response
        response_data = {
            "data": serializer.data,         # complete serialized data
            "host_name": host_name,          # host first name
            "email": host_email,             # email from query
            "host_image": host_image,        # profile image
            "is_verified": is_verified       # verification status
        }
        return Response(response_data, status=200)
# =================== """" END HAER """""" ========================

# ====== ** HOST APNI PROPERTY ADD KER SAKTA HAI VARIFEID HONE BAAD ** ====== // 
@api_view(['POST'])
def host_Add_His_Property(request):
    try:
        print("\n#======= POST REQUEST HOST ADD PROPERTY ========#")
        host_email = request.data.get('hostEmail') 
        host_detail = request.data.get('handleInput')
        user = CustomUser.objects.get(email=host_email)
        host_profile = HostProfile.objects.get(host=user)
        def to_bool(val):
            return str(val).lower() in ["true", "1", "on", "yes"]

        category_id = host_detail.get('homeType', None)
        category_instance = None
        if category_id:
            try:
                category_instance = CategoryOfServices.objects.get(id=category_id)
            except CategoryOfServices.DoesNotExist:
                category_instance = None

        ListingProperty.objects.create(
            host=host_profile,
            category=category_instance,
            title=host_detail.get('hometitle', ''),
            description=host_detail.get('homeDiscriptions', ''),
            price_per_night=host_detail.get('homePricePerNight', 0),
            location=host_detail.get('homeAdress', ''),
            city=host_detail.get('homeCity', ''),
            country=host_detail.get('homeCountry', ''),
            pincode=host_detail.get('homePin', ''),
            guests_allowed=host_detail.get('homeTotalGuest', 1),
            bedrooms=host_detail.get('homeBads', 1),
            bathrooms=host_detail.get('homeBathrooms', 1),
            beds=host_detail.get('homeBads', 1),

            # ✅ Convert checkbox strings to boolean
            wifi=to_bool(host_detail.get('homeWifi')),
            pools=to_bool(host_detail.get('homePool')),
            gym=to_bool(host_detail.get('homeGym')),
            pickupFacility=to_bool(host_detail.get('homePickup')),
            smoking=to_bool(host_detail.get('homeSmooking')),
            food=to_bool(host_detail.get('homeFood')),
            parking=to_bool(host_detail.get('homeParking')),
            securityCam=to_bool(host_detail.get('homeCameras')),
            tv=to_bool(host_detail.get('homeTV')),
            Ac=to_bool(host_detail.get('homeAC')),
            filterWater=to_bool(host_detail.get('homeFilterWater')),
            StayLongAllow=to_bool(host_detail.get('homeStayLong')),

            available_from=host_detail.get('homeAvailableDateFrom'),
            available_to=host_detail.get('homeAvailableDateTo'),
        )

        print("✅ Property successfully added!")
        return Response(status=200)

    except CustomUser.DoesNotExist:
        return Response(status=401)

    except HostProfile.DoesNotExist:
        return Response(status=401)

    except Exception as e:
        print("❌ Error:", e)
        return Response({"error": str(e)}, status=500)
# =================== """" END HAER """""" ========================

# ====== ** YAHA SE PROPERTY FILLTER HO KE JA RAHI HAI** ====== // 
from .serializers import ListingPropertySerializer
@api_view(['GET'])
def host_Get_His_Property_Datails(request):
    host_email = request.query_params.get('email')
    properties = ListingProperty.objects.filter(host__host__email=host_email)
    serializer = ListingPropertySerializer(properties, many=True, context={'request': request})
    return Response(serializer.data)
# =================== """" END HAER """""" ========================

# ====== ** YAHA SE PROPERTY FILLTER HO KE JA RAHI HAI** ====== // 
@api_view(['POST'])
def host_add_his_Property_Image(request):
    host_email = request.data.get('hostEmail')
    host_selected_Property = request.data.get('selectedProperty')
    host_selected_Image = request.FILES.get('selectedFile')

    try:
        property_instance = ListingProperty.objects.get(id=host_selected_Property)

        PropertyImage.objects.create(
            Owner=host_email,
            property=property_instance,
            image=host_selected_Image
        )
        return Response({"status": "success", "message": "Image uploaded successfully!"})

    except ListingProperty.DoesNotExist:
        return Response({"status": "error", "message": "Property not found!"}, status=404)

    except Exception as e:
        print("Error:", e)
        return Response({"status": "error", "message": str(e)}, status=500)
# =================== """" END HAER """""" ========================

# 📍📍📍📍📍📍📍📍📍📍📍📍📍📍📍📍📍📍📍📍📍📍📍📍📍📍📍📍📍📍📍📍📍📍📍📍
# ====== ** YAHA SE IMAGE OR PROPERTY FILLTER HO KE JA RAHI HAI** ====== // 
from .serializers import PropertyWithImagesSerializer
@api_view(['GET'])
def host_property_details_with_images(request):
    email = request.GET.get('email')
    if not email:
        return Response({"error": "Email is required"}, status=400)
    # Filter properties belonging to the Host
    properties = ListingProperty.objects.filter(host__host__email=email)
    serializer = PropertyWithImagesSerializer(properties, many=True, context={'request': request})
    return Response(serializer.data)
# =================== """" END HAER """""" ========================

# ====== ** YAHA SE PROPERTY FILLTER HO KE MANAGE PROPERTY ME JA RAHI HAI** ====== // 
@api_view(['GET'])
def host_Manage_All_Property_Details(request):
    email = request.GET.get('email')
    if not email:
        return Response({"error": "Email is required"}, status=400)
    properties = ListingProperty.objects.filter(host__host__email=email)
    if not properties.exists():
        return Response([], status=200)
    serializer = PropertyWithImagesSerializer(properties, many=True, context={'request': request})
    return Response(serializer.data)
# =================== """" END HAER """""" ========================

# ====== ** YAHA SE PROPERTY EDIT BTN ME CLICK KER DETAILS NEW PAGE ME AA RAHI HAI ** ====== // 
@api_view(['GET', 'PUT'])
def host_Edit_BTN_Property_All_Fun(request, pk):
    try:
        property_obj = ListingProperty.objects.get(id=pk)
    except ListingProperty.DoesNotExist:
        return Response({"error": "Property not found"}, status=404)

    if request.method == 'GET':
        serializer = PropertyWithImagesSerializer(property_obj, context={'request': request})
        return Response(serializer.data, status=200)

    elif request.method == 'PUT':
        serializer = PropertyWithImagesSerializer(property_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        print(serializer.errors)
        return Response(serializer.errors, status=400)
# =================== """" END HAER """""" ========================

# ====== ** YAHA SE HOST DASHBORD KI SARI DETAILS AATI HAI ** ====== // 
@api_view(['GET'])
def host_Dashboard(request, pk):
    bookings = Booking.objects.filter(property__host__host__email=pk)
    serializer = BookingSerializer(
        bookings,
        many=True,
        context={"request": request}
    )

    return Response({
        "bookings": serializer.data,
        "count": bookings.count(),
        "message": "API called successfully"
    })
# =================== """" END HAER """""" ========================

# ====== ** YAHA SE HOST DASHBORD KI SARI DETAILS AATI HAI ** ====== // 
@api_view(['PUT'])
def Host_Approvel_Process(request,id):
    booking = get_object_or_404(Booking, id=id)
    print("Booking Id : ",booking)
    process = request.data.get("Process")
    if not process:
        return Response(
            {"msg": "Process field is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    booking.status = process.upper().strip()
    booking.save()

    return Response({
        "booking_id": booking.id,
        "status": booking.status,
        "msg": "Booking updated successfully!"
    }, status=status.HTTP_200_OK)
# =================== """" END HAER """""" ========================











# ************ USER KO SAREN CARD DIKHENGE *****************
@api_view(['GET'])
def User_Showing_All_Cards(request):
    properties = ListingProperty.objects.all()
    serializer = PropertyWithImagesSerializer(properties, many=True, context={'request': request})
    return Response(serializer.data)  
# **********************************************************

# ************ EK CARD KO DETAILS SHOW *********************
@api_view(['GET'])
def User_Show_All_Details_Of_Particuler_Card(request, id):
    try:
        property_obj = ListingProperty.objects.get(id=id)
        serializer = PropertyWithImagesSerializer(property_obj, context={'request': request})
        return Response(serializer.data)
    except ListingProperty.DoesNotExist:
        return Response({"error": "Property not found"}, status=404)
# **********************************************************

# ************** SEARCH KI REQUEST KE LIYE ******************
@api_view(['GET'])
def Search_Request(request):
    location = request.GET.get('location')
    popules = request.GET.get('popules')

    if not location:
        return Response(status=400)
    
    if not popules:
        return Response(status=400)

    try:
        popules_int = int(popules)
    except ValueError:
        return Response(status=401)

    properties = ListingProperty.objects.filter(
        city__icontains=location,
        guests_allowed__gte=popules_int
    )
    if not properties.exists():
        return Response([],status=200)

    serializer = PropertyWithImagesSerializer(properties, many=True, context={'request': request})
    return Response(serializer.data)
# **********************************************************


# # ************* USER KE SIGNUP KE LIYE HAI **************
@api_view(['POST'])
def User_Registration(request):
    try:
        data = request.data
        files = request.FILES

        # Required fields
        required_fields = ['firstName', 'lastName', 'email', 'phone', 'password', 'address', 'as_user']
        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            return Response({
                "status": False,
                "message": f"Missing required fields: {', '.join(missing)}"
            }, status=400)

        # Check duplicates
        if CustomUser.objects.filter(email=data.get('email')).exists():
            return Response({"status": False, "message": "Email already registered"}, status=400)

        if CustomUser.objects.filter(phone=data.get('phone')).exists():
            return Response({"status": False, "message": "Phone number already registered"}, status=400)

        # Parse boolean
        as_user_value = str(data.get('as_user')).lower() == "true"

        # Create user
        user = CustomUser(
            first_name = data.get('firstName').strip(),
            last_name  = data.get('lastName').strip(),
            email      = data.get('email').lower().strip(),
            phone      = data.get('phone').strip(),
            address    = data.get('address').strip(),
            as_user    = as_user_value,
            as_host    = False,
            image      = files.get('profile_image') if 'profile_image' in files else None,
            password   = data.get('password')  # raw password
        )
        user.save()


        return Response({
            "status": True,
            "message": "User registered successfully!",
            "user_id": user.id
        }, status=201)

    except Exception as e:
        return Response({
            "status": False,
            "message": "Something went wrong!",
            "error": str(e)
        }, status=500)
# **********************************************************

# # ************* USER KE LOGIN KE LIYE HAI *****************
import json
@api_view(['POST'])
def User_Login(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except:
        return Response({"error": "Invalid JSON format"}, status=400)
    email = data.get("email")
    password = data.get("Password")
    if not email or not password:
        return Response({"error": "Email and Password are required"}, status=400)
    try:
        user = CustomUser.objects.get(email=email, password=password)
        return Response({
            "message": "Login Successful",
            "user_id": user.id,
            "user_name": user.first_name,
            "user_last_name": user.last_name,
            "user_email": user.email,
            "user_phone": user.phone,
        }, status=200)
    except CustomUser.DoesNotExist:
        return Response({"error": "Invalid email or password"}, status=401)
# **********************************************************

# # ************* USER WISHLIST ADD KAREGA *****************
@api_view(['POST', 'GET'])
def User_Wishlist(request):
    if request.method == "POST":
        data = json.loads(request.body) 
        user_id = data.get("userId")
        product_id = data.get("productId")

        user = CustomUser.objects.get(id=user_id)
        product = ListingProperty.objects.get(id=product_id)

        isproductFind = AddToWishList.objects.filter(user=user, property=product).first()
        if isproductFind:
            return Response({"status": "exists", "message": "Already in wishlist"}, status=400)
        else:
            AddToWishList.objects.create(
                user=user,
                property=product,
                added_at=timezone.now()
            )
            return Response({"status": "success", "message": "Added to wishlist"}, status=200)
    return Response({"status": "success", "userId": user_id, "productId": product_id})
# **********************************************************


# ************* USER WISHLIST FATCH KAREGA *****************
from .serializers import WishListSerializer
@api_view(['GET'])
def User_Wishlist_Fatch(request, id):
    wishlist = AddToWishList.objects.filter(user_id=id)
    serializer = WishListSerializer(wishlist, many=True, context={"request": request})
    return Response({
        "status": True,
        "count": wishlist.count(),
        "wishlist": serializer.data
    })
# **********************************************************

# ************* USER Expiriance Cards **********************
@api_view(['GET'])
def Experience(request, pk):
    try:
        category = CategoryOfServices.objects.get(services_name=pk)
    except CategoryOfServices.DoesNotExist:
        return Response({"message": "Category not found"}, status=404)
    properties = ListingProperty.objects.filter(category=category)
    serializer = PropertyWithImagesSerializer(properties, many=True,context={'request': request})
    return Response(serializer.data)
# **********************************************************




# ************* USER HOMES Cards **********************
@api_view(['GET'])
def Home(request,pk):
    properties = ListingProperty.objects.all()
    serializer = PropertyWithImagesSerializer(properties, many=True,context={'request': request})
    return Response(serializer.data)
# **********************************************************



# ************* USER HOMES Cards **********************
@api_view(['GET'])
def Services(request, pk):
    try:
        category = CategoryOfServices.objects.get(services_name=pk)
    except CategoryOfServices.DoesNotExist:
        return Response({"message": "Category not found"}, status=404)
    properties = ListingProperty.objects.filter(category=category)
    serializer = PropertyWithImagesSerializer(properties, many=True,context={'request': request})
    return Response(serializer.data)
# **********************************************************


# ************* USER RAZORPAY **********************
# initialize razorpay client
RAZORPAY_KEY_ID = getattr(settings, "RAZORPAY_KEY_ID", None)
RAZORPAY_KEY_SECRET = getattr(settings, "RAZORPAY_KEY_SECRET", None)
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

@api_view(['POST'])
def create_razorpay_order(request):
    """
    Expects: property_id, check_in (YYYY-MM-DD), check_out (YYYY-MM-DD), guests, user_id
    Returns order info for frontend Razorpay checkout
    """
    serializer = CreateOrderSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    prop = get_object_or_404(ListingProperty, id=data['property_id'])
    user = get_object_or_404(CustomUser, id=data['user_id'])

    # Calculate nights
    from datetime import datetime
    start = datetime.strptime(str(data['check_in']), "%Y-%m-%d").date()
    end = datetime.strptime(str(data['check_out']), "%Y-%m-%d").date()
    nights = (end - start).days
    if nights <= 0:
        nights = 1

    # price calculation (reuse your logic)
    price_per_night = Decimal(prop.price_per_night)
    base_price = price_per_night * nights
    extra_guest_charge = (data['guests'] - 1) * Decimal(200) if data['guests'] > 1 else Decimal(0)
    total_amt = base_price + extra_guest_charge
    # Razorpay uses paise (INR) as integer

    amount_paise = int(total_amt * 100)

    if amount_paise < 100:
        amount_paise = 100   # Razorpay minimum amount


    # Create a pending Booking in DB
    booking = Booking.objects.create(
        user=user,
        property=prop,
        check_in=data['check_in'],
        check_out=data['check_out'],
        guests=data['guests'],
        nights=nights,
        total_amount=total_amt,
        currency="INR",
        status="pending"
    )

    # Create Razorpay Order
    razorpay_order = client.order.create(dict(amount=amount_paise, currency="INR", payment_capture=1))
    # Save Payment record with order id
    payment = Payment.objects.create(
        booking=booking,
        razorpay_order_id=razorpay_order['id'],
        amount=total_amt,
        currency="INR",
        captured=False
    )

    # Prepare data to send to frontend
    return Response({
        "order_id": razorpay_order['id'],
        "amount": razorpay_order['amount'],
        "currency": razorpay_order['currency'],
        "booking_id": booking.id,
        "razorpay_key_id": RAZORPAY_KEY_ID,
        "customer": {
            "name": f"{user.first_name} {user.last_name}",
            "email": user.email,
            "contact": user.phone
        }
    })
# **********************************************************



# ************* USER RAZORPAY VARIFY PAYMENT **********************
@api_view(['POST'])
@csrf_exempt
def verify_payment(request):
    print("****************verify_payment****************")
    """
    Called by frontend on successful payment. Verifies signature and updates records.
    Expects: razorpay_payment_id, razorpay_order_id, razorpay_signature, booking_id
    """
    payload = request.data
    required = ("razorpay_payment_id", "razorpay_order_id", "razorpay_signature", "booking_id")
    if not all(k in payload for k in required):
        return Response({"detail": "Missing parameters"}, status=status.HTTP_400_BAD_REQUEST)

    razorpay_payment_id = payload['razorpay_payment_id']
    razorpay_order_id = payload['razorpay_order_id']
    razorpay_signature = payload['razorpay_signature']
    booking_id = payload['booking_id']

    # Verify signature (HMAC SHA256)
    generated_signature = hmac.new(
        bytes(RAZORPAY_KEY_SECRET, 'utf-8'),
        msg=bytes(razorpay_order_id + "|" + razorpay_payment_id, 'utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

    if generated_signature != razorpay_signature:
        return Response({"detail": "Signature verification failed"}, status=status.HTTP_400_BAD_REQUEST)

    # Update payment and booking
    try:
        payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
    except Payment.DoesNotExist:
        return Response({"detail": "Payment record not found"}, status=status.HTTP_404_NOT_FOUND)

    payment.razorpay_payment_id = razorpay_payment_id
    payment.razorpay_signature = razorpay_signature
    payment.captured = True
    payment.save()

    booking = payment.booking
    booking.status = "confirmed"
    booking.save()

    return Response({"detail": "Payment verified and booking confirmed", "booking_id": booking.id})
# **********************************************************

# ************* USER TRACK BOOKING  **********************
from .serializers import BookingSerializer
@api_view(['GET'])
def User_Track_Booking(request, id, nm):
    if not id and not nm:
        return Response({"error": "User is not logged in, please login"}, status=401)

    booking_details = Booking.objects.filter(user_id=id)
    # 🔥 FIX: pass context with request
    serializer = BookingSerializer(
        booking_details,
        many=True,
        context={'request': request}
    )
    return Response(serializer.data, status=200)
# **********************************************************


# ************* USER Property Comments  ********************
@api_view(['POST'])
def User_Comments(request):
    data = request.data
    comment = data.get('comment')
    host_id = data.get('host_Id')
    property_id = data.get('property_id')
    host_name = data.get('host_name')
    host_phone = data.get('host_phone')
    userActualID = data.get('userActualID')
    
    host = get_object_or_404(HostProfile, id=host_id)
    property_obj = get_object_or_404(ListingProperty, id=property_id)

    # 🔥 IMPORTANT FIX
    user = get_object_or_404(CustomUser, id=userActualID)

    feedback = UserFeedback.objects.create(
        host=host,
        user=user,              # ✅ CustomUser object
        property=property_obj,
        host_name=host_name,
        message=comment,
        phone=host_phone
    )

    print(feedback)

    return Response(
        {"message": "Feedback created successfully"},
        status=201
    )
# **********************************************************



from .serializers import UserFeedbackSerializer
@api_view(['GET'])
def User_Read_Comments(request, pk):
    # ✅ ONLY comments of this property
    comments = UserFeedback.objects.filter(property_id=pk)

    serializer = UserFeedbackSerializer(comments, many=True)

    return Response({
        "property_id": pk,
        "total_comments": comments.count(),
        "comments": serializer.data
    })









from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def User_Reported_Host(request):
    data = request.data

    report_reason = data.get("report_reason")
    other_reason = data.get("other_reason", "")
    host_id = data.get("host_id")
    user_id = data.get("user_id")

    if not report_reason or not host_id or not user_id:
        return Response(
            {"error": "Missing required fields"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        host = HostProfile.objects.get(id=host_id)
        user = CustomUser.objects.get(id=user_id)
    except HostProfile.DoesNotExist:
        return Response({"error": "Host not found"}, status=404)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    reason = other_reason if report_reason == "other" else report_reason

    UserReportSectionOfHost.objects.create(
        host=host,
        user=user,
        reason=reason,
        is_resolved=False,
        report_count=1
    )

    return Response(
        {"message": "Host reported successfully"},
        status=status.HTTP_201_CREATED
    )



# ************** Admin Login ********************************
from django.contrib.auth.models import User
@api_view(['POST'])
def Admin_login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    print("***************")
    print(email, " : ", password)

    if not email or not password:
        return Response({"error": "Email and password are required"}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "Invalid credentials or not an admin/staff"}, status=401)

    if user.check_password(password) and (user.is_superuser or user.is_staff):
        return Response({"message": "Login successful"}, status=200)
    else:
        print("Last Vala ************************")
        return Response({"error": "Invalid credentials or not an admin/staff"}, status=401)
# ****************************************************************



# ************** Admin All Dasboerd ******************************
from .serializers import BookingSerializer,CustomUserSerializer
from django.db.models import Sum
@api_view(['GET'])
def Admin_Booking(request):
    booking_details = Booking.objects.all()
    serializer = BookingSerializer(
        booking_details,
        many=True,
        context={'request': request}
    )

    total_revenue = Booking.objects.aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    return Response({
        "bookings": serializer.data,
        "total_bookings": booking_details.count(),
        "total_revenue": total_revenue
    }, status=200)

@api_view(['GET'])
def Admin_Users(request):
    users = CustomUser.objects.filter(as_host=True)
    serializer = CustomUserSerializer(users ,many=True)    
    return Response(serializer.data)
# ****************************************************************

# ************** Admin Manage All Booking ************************
@api_view(['GET'])
def Admin_Mange_Booking(request):
    bookings = Booking.objects.all()
    serializer = BookingSerializer(
        bookings,
        many=True,
        context={"request": request}
    )
    return Response({
        "bookings": serializer.data,
        "count": bookings.count(),
        "message": "API called successfully"
    })
# ****************************************************************

# ************** Admin Manage All Users **************************
@api_view(['GET'])
def Admin_Mange_Users(request): 
    users = HostProfile.objects.filter(host__as_host=True)
    serializer = HostProfileSerializer(users, many=True)
    print(serializer.data)
    return Response(serializer.data, status=200)
# ****************************************************************


# ************** Admin Verifying Host  ***************************
@api_view(['PUT'])
def Admin_Varified_Host(request, pk):
    try:
        host_profile = HostProfile.objects.get(id=pk)
        host_profile.verified_status = True
        host_profile.save()
        return Response(
            {"message": "Host verified successfully"},status=200)
    except HostProfile.DoesNotExist:
        return Response({"error": "Host profile not found"},status=404)
# ****************************************************************



# ************** Admin Deleted Host profile **********************
@api_view(['DELETE'])
def Admin_Varified_Delete(request, pk):
    try:
        host_profile = HostProfile.objects.get(id=pk)
        host_profile.delete()  
        return Response({"message": "Host Deleted successfully"},status=200)
    except HostProfile.DoesNotExist:
        return Response({"error": "Host profile not found"},status=404)
# ****************************************************************


# ************** Admin Get All Host Details **********************
@api_view(['GET'])
def Admin_Mange_Host(request):
    all_hosts = HostProfile.objects.all()
    serializer = HostProfileSerializer(all_hosts, many=True)
    return Response(serializer.data, status=200)
# ****************************************************************


# ************** Admin Update All Host Details********************
@api_view(['PATCH'])
def Admin_Update_Host_Details(request, id):
    host_profile = HostProfile.objects.get(id=id)
    data = request.data

    # 🔹 Host data
    host_data = data.get('host', {})

    host = host_profile.host
    host.first_name = host_data.get('first_name', host.first_name)
    host.last_name  = host_data.get('last_name', host.last_name)
    host.email      = host_data.get('email', host.email)
    host.phone      = host_data.get('phone', host.phone)
    host.address    = host_data.get('address', host.address)
    host.save()

    # 🔹 HostProfile data
    host_profile.bio = data.get('bio', host_profile.bio)
    host_profile.govt_id_type = data.get('govt_id_type', host_profile.govt_id_type)
    host_profile.govt_id_number = data.get('govt_id_number', host_profile.govt_id_number)
    host_profile.address = data.get('address', host_profile.address)
    host_profile.city = data.get('city', host_profile.city)
    host_profile.country = data.get('country', host_profile.country)
    host_profile.verified_status = data.get('verified_status', host_profile.verified_status)

    host_profile.save()

    return Response({"message": "Host updated successfully"}, status=200)


# ****************************************************************



# ************** Admin Manage Host Security ********************
from .serializers import HostLoginDetailsHistorySerializer
@api_view(['GET'])
def Admin_Manage_Login_History(request):
    history = HostLoginDetailsHistory.objects.all().order_by('-login_time')
    serializer = HostLoginDetailsHistorySerializer(history, many=True)
    return Response(serializer.data, status=200)
# ****************************************************************





# ************** Admin Manage Host Security ********************
from .serializers import PaymentSerializer
@api_view(['GET'])
def Admin_Manage_Paymets(request):
    payments = Payment.objects.all()
    serializer = PaymentSerializer(
        payments,
        many=True,
        context={'request': request}   # IMPORTANT
    )
    return Response(serializer.data)
# ****************************************************************




@api_view(['POST'])
def Admin_Approved_Swich(request):
    data = request.data

    obj = AdminAllMutedFiledSwich.objects.create(
        muteAddProperty=data.get("muteAddProperty") == "on",
        muteAddServices=data.get("muteAddServices") == "on",
        muteEdit=data.get("muteEdit") == "on",
        muteNotifications=data.get("muteNotifications") == "on",
        muteNotificationManageMent=data.get("muteNotificationManageMent") == "on",
    )
    return Response({
        "message": "Settings saved",
        "id": obj.id
    })





from .serializers import AdminAllMutedFiledSwichSerializer

@api_view(['GET'])
def Admin_Alllow(request):
    instance = AdminAllMutedFiledSwich.objects.last()
    if not instance:
        return Response({"message": "No settings found"},status=404)
    serializer = AdminAllMutedFiledSwichSerializer(instance)
    return Response(serializer.data)









from .models import UserReportSectionOfHost
from .serializers import UserReportSectionOfHostSerializer

@api_view(['GET'])
def Admin_Manage_FeedBack(request):
    reports = UserReportSectionOfHost.objects.all()
    serializer = UserReportSectionOfHostSerializer(reports, many=True)
    return Response(serializer.data)








# @api_view(['GET'])
# def Admin_Mange_Refunds(request):
#     booking = Booking.objects.filter(status="CANCEL")
#     serialize = BookingSerializer(booking,many=True)
#     return Response(serialize.data)


























from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import transaction
from .models import Booking, Payment, Refund, CustomUser, ListingProperty
from django.utils import timezone
from django.shortcuts import get_object_or_404
from decimal import Decimal

@csrf_exempt
def admin_booking_list(request):
    """
    Get all bookings for admin refund management
    """
    if request.method == "GET":
        try:
            # Get all bookings with related data
            bookings = Booking.objects.select_related(
                'user', 'property'
            ).all().order_by('-created_at')
            
            # Serialize data
            serialized_bookings = []
            for booking in bookings:
                # Calculate refund amount (80% of total)
                try:
                    refund_amount = float(booking.total_amount) * 0.8
                except:
                    refund_amount = 0
                
                booking_data = {
                    'id': booking.id,
                    'user': {
                        'id': booking.user.id,
                        'first_name': booking.user.first_name,
                        'last_name': booking.user.last_name,
                        'email': booking.user.email,
                        'phone': booking.user.phone,
                    },
                    'property': {
                        'id': booking.property.id,
                        'title': booking.property.title,
                        'city': booking.property.city,
                    },
                    'check_in': booking.check_in.strftime('%Y-%m-%d') if booking.check_in else None,
                    'check_out': booking.check_out.strftime('%Y-%m-%d') if booking.check_out else None,
                    'total_amount': float(booking.total_amount) if booking.total_amount else 0,
                    'refund_amount': round(refund_amount, 2),
                    'status': booking.status,
                    'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M:%S') if booking.created_at else None,
                }
                serialized_bookings.append(booking_data)
            
            return JsonResponse({
                'success': True,
                'message': 'Bookings fetched successfully',
                'bookings': serialized_bookings
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Failed to fetch bookings',
                'error': str(e)
            }, status=400)
    else:
        return JsonResponse({
            'success': False,
            'message': 'Method not allowed'
        }, status=405)

@csrf_exempt
def admin_refund_list(request):
    """
    Get list of canceled bookings eligible for refund
    """
    if request.method == "GET":
        try:
            # Get canceled bookings
            canceled_bookings = Booking.objects.filter(status="cancelled").select_related(
                'user', 'property'
            ).order_by('-created_at')
            
            # Check which bookings already have refunds
            refunded_booking_ids = Refund.objects.filter(
                booking__in=canceled_bookings
            ).values_list('booking_id', flat=True)
            
            # Filter out bookings that already have refunds
            pending_refunds = []
            for booking in canceled_bookings:
                if booking.id not in refunded_booking_ids:
                    try:
                        refund_amount = float(booking.total_amount) * 0.8
                    except:
                        refund_amount = 0
                    
                    pending_refunds.append({
                        'id': booking.id,
                        'user': {
                            'id': booking.user.id,
                            'name': f"{booking.user.first_name} {booking.user.last_name}",
                            'email': booking.user.email,
                            'phone': booking.user.phone,
                        },
                        'property': {
                            'id': booking.property.id,
                            'title': booking.property.title,
                            'city': booking.property.city,
                        },
                        'check_in': booking.check_in.strftime('%Y-%m-%d'),
                        'check_out': booking.check_out.strftime('%Y-%m-%d'),
                        'total_amount': float(booking.total_amount) if booking.total_amount else 0,
                        'refund_amount': round(refund_amount, 2),
                        'booking_date': booking.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    })
            
            return JsonResponse({
                'success': True,
                'message': 'Pending refunds fetched successfully',
                'pending_refunds': pending_refunds,
                'count': len(pending_refunds)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Failed to fetch refund list',
                'error': str(e)
            }, status=400)
    else:
        return JsonResponse({
            'success': False,
            'message': 'Method not allowed'
        }, status=405)

@csrf_exempt
def update_refund_status(request):
    """
    Update refund status for a booking
    """
    if request.method == "POST":
        try:
            # Parse JSON data
            try:
                data = json.loads(request.body.decode('utf-8'))
            except:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid JSON data'
                }, status=400)
            
            booking_id = data.get('bookingId')
            status_value = data.get('status', 'REFUNDED')
            refund_amount = data.get('refundAmount')
            refund_method = data.get('refundMethod', 'system')
            transaction_id = data.get('transactionId')
            
            # Validate required fields
            if not booking_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Booking ID is required'
                }, status=400)
            
            if not refund_amount:
                return JsonResponse({
                    'success': False,
                    'message': 'Refund amount is required'
                }, status=400)
            
            with transaction.atomic():
                # Get booking
                try:
                    booking = Booking.objects.get(id=booking_id)
                except Booking.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': f'Booking with id {booking_id} not found'
                    }, status=404)
                
                # Get payment for this booking (optional)
                payment = Payment.objects.filter(booking=booking).first()
                
                # Update booking status
                booking.status = 'refunded'  # Always set to lowercase 'refunded'
                booking.save()
                
                # Generate transaction ID if not provided
                if not transaction_id:
                    transaction_id = f"REF{booking_id}{int(timezone.now().timestamp())}"
                
                # Convert refund amount to Decimal
                try:
                    refund_amount_decimal = Decimal(str(refund_amount))
                except:
                    refund_amount_decimal = Decimal('0.00')
                
                # Create or update refund record
                try:
                    existing_refund = Refund.objects.get(booking=booking)
                    
                    # Update existing refund
                    existing_refund.refund_amount = refund_amount_decimal
                    existing_refund.refund_method = refund_method
                    existing_refund.status = 'completed'
                    existing_refund.transaction_id = transaction_id
                    
                    if payment:
                        existing_refund.payment = payment
                    
                    # Optional bank details
                    if data.get('bankAccount'):
                        existing_refund.bank_account = data.get('bankAccount')
                    if data.get('ifscCode'):
                        existing_refund.ifsc_code = data.get('ifscCode')
                    if data.get('upiId'):
                        existing_refund.upi_id = data.get('upiId')
                    
                    existing_refund.notes = data.get('notes', 'Refund processed via admin panel')
                    existing_refund.save()
                    
                    refund = existing_refund
                    created = False
                    
                except Refund.DoesNotExist:
                    # Create new refund record
                    refund = Refund.objects.create(
                        booking=booking,
                        payment=payment,
                        user=booking.user,
                        refund_amount=refund_amount_decimal,
                        refund_method=refund_method,
                        status='completed',
                        transaction_id=transaction_id,
                        notes=data.get('notes', 'Refund processed via admin panel')
                    )
                    created = True
                
                return JsonResponse({
                    'success': True,
                    'message': 'Refund status updated successfully',
                    'refund_id': refund.id,
                    'transaction_id': refund.transaction_id,
                    'booking_id': booking_id,
                    'refund_amount': float(refund_amount_decimal),
                    'status': status_value,
                    'created': created
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Failed to update refund status',
                'error': str(e)
            }, status=400)
    else:
        return JsonResponse({
            'success': False,
            'message': 'Method not allowed'
        }, status=405)

@csrf_exempt
def process_refund(request):
    """
    Process a refund request
    """
    if request.method == "POST":
        try:
            # Parse JSON data
            try:
                data = json.loads(request.body.decode('utf-8'))
            except:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid JSON data'
                }, status=400)
            
            booking_id = data.get('bookingId')
            refund_amount = data.get('refundAmount')
            
            # Validate required fields
            if not booking_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Booking ID is required'
                }, status=400)
            
            if not refund_amount:
                return JsonResponse({
                    'success': False,
                    'message': 'Refund amount is required'
                }, status=400)
            
            # Validate booking exists
            try:
                booking = Booking.objects.get(id=booking_id)
            except Booking.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Booking not found'
                }, status=404)
            
            # Check if refund already exists
            if hasattr(booking, 'refund'):
                return JsonResponse({
                    'success': False,
                    'message': 'Refund already processed for this booking'
                }, status=400)
            
            # Generate transaction ID
            transaction_id = f"TXN{booking_id}{int(timezone.now().timestamp())}"
            
            return JsonResponse({
                'success': True,
                'message': 'Refund processed successfully',
                'transaction_id': transaction_id,
                'refund_amount': refund_amount,
                'booking_id': booking_id,
                'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Failed to process refund',
                'error': str(e)
            }, status=400)
    else:
        return JsonResponse({
            'success': False,
            'message': 'Method not allowed'
        }, status=405)

@csrf_exempt
def refund_details(request, booking_id):
    """
    Get refund details for a specific booking
    """
    if request.method == "GET":
        try:
            # Get booking
            try:
                booking = Booking.objects.get(id=booking_id)
            except Booking.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Booking not found'
                }, status=404)
            
            # Check if refund exists
            refund_data = None
            try:
                refund = Refund.objects.get(booking=booking)
                refund_data = {
                    'id': refund.id,
                    'refund_amount': float(refund.refund_amount) if refund.refund_amount else 0,
                    'refund_method': refund.refund_method,
                    'status': refund.status,
                    'transaction_id': refund.transaction_id,
                    'admin_comment': refund.admin_comment,
                    'created_at': refund.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'refund_date': refund.refund_date.strftime('%Y-%m-%d %H:%M:%S') if refund.refund_date else None,
                }
            except Refund.DoesNotExist:
                refund_data = None
            
            # Calculate suggested refund amount (80% of total)
            try:
                suggested_refund = float(booking.total_amount) * 0.8
            except:
                suggested_refund = 0
            
            # Prepare booking details
            booking_details = {
                'id': booking.id,
                'user_name': f"{booking.user.first_name} {booking.user.last_name}",
                'user_email': booking.user.email,
                'user_phone': booking.user.phone,
                'property_title': booking.property.title,
                'property_city': booking.property.city,
                'check_in': booking.check_in.strftime('%Y-%m-%d') if booking.check_in else None,
                'check_out': booking.check_out.strftime('%Y-%m-%d') if booking.check_out else None,
                'total_amount': float(booking.total_amount) if booking.total_amount else 0,
                'status': booking.status,
                'booking_date': booking.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            
            return JsonResponse({
                'success': True,
                'message': 'Refund details fetched successfully',
                'booking': booking_details,
                'suggested_refund': round(suggested_refund, 2),
                'existing_refund': refund_data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Failed to fetch refund details',
                'error': str(e)
            }, status=400)
    else:
        return JsonResponse({
            'success': False,
            'message': 'Method not allowed'
        }, status=405)
    






from django.utils.timezone import now
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import HostProfile, ListingProperty, PaymentsForHostByAdmin
from .serializers import AdminHostSalarySerializer



@api_view(['GET'])
def Admin_Fetch_All_Host_Details(request):

    current_month = now().month
    current_year = now().year

    COMMISSION_PER_PROPERTY = 500
    PENALTY_PER_REPORT = 100

    results = []
    hosts = HostProfile.objects.select_related("host")

    for host in hosts:
        report_count = UserReportSectionOfHost.objects.filter(host=host).count()
        property_count = ListingProperty.objects.filter(host=host).count()

        total_commission = property_count * COMMISSION_PER_PROPERTY
        penalty_amount = report_count * PENALTY_PER_REPORT

        final_payout = total_commission - penalty_amount
        if final_payout < 0:
            final_payout = 0  # ✅ safety

        payment_obj, created = PaymentsForHostByAdmin.objects.get_or_create(
            host=host,
            month=current_month,
            year=current_year,
            defaults={
                "total_properties": property_count,
                "report_count": report_count,
                "commission_per_property": COMMISSION_PER_PROPERTY,
                "total_commission": total_commission,
                "penalty": penalty_amount,
                "final_payout": final_payout,
            }
        )

        if not created:
            payment_obj.total_properties = property_count
            payment_obj.report_count = report_count
            payment_obj.total_commission = total_commission
            payment_obj.penalty = penalty_amount
            payment_obj.final_payout = final_payout
            payment_obj.save()

        results.append(payment_obj)

    serializer = AdminHostSalarySerializer(results, many=True)
    return Response(serializer.data)











import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def create_payment_intent(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)

        amount = data.get("amount")
        host_id = data.get("hostId")
        host_email = data.get("hostEmail")

        if not amount:
            return JsonResponse({"error": "Amount is required"}, status=400)

        # ✅ Create Stripe PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=int(amount),  # in paise
            currency="inr",
            receipt_email=host_email,
            metadata={
                "host_id": host_id,
                "type": "host_salary",
            },
        )

        return JsonResponse({
            "success": True,
            "clientSecret": intent.client_secret,
            "paymentIntentId": intent.id,
        })

    except stripe.error.StripeError as e:
        return JsonResponse({
            "error": str(e)
        }, status=400)

    except Exception as e:
        return JsonResponse({
            "error": str(e)
        }, status=500)




















































