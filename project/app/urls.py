from django.contrib import admin
from django.urls import path,include
from .views import *
urlpatterns = [
   path('host-login/',host_login_api),
   path('host-Addservices/',host_addservices),
   path('host-ManageServices/',host_manageServices),
   path('host-Manage-Profile/',host_Profile),
   path('Show-All-Servises/', ShowAll_Category_In_Select_Tag),
   path('Check-Host-Varifeid/',IsHostVarifeid),
   path('host-Add-Property/',host_Add_His_Property),
   path('host-Get-Property-Details/',host_Get_His_Property_Datails),     # YAHA SE SARI PROPERTY DETAILS NIKAL RAHE HAI JO HOST NE ADD KI HAI
   path('host-Add-Property-Image/',host_add_his_Property_Image),
   path("host-property-details-with-images/", host_property_details_with_images),
   path("host-Manage-Property-All/",host_Manage_All_Property_Details),
   path('host-Edit-BTN-Property-All/<int:pk>/', host_Edit_BTN_Property_All_Fun),
   path('Host-Dashboard/<str:pk>/',host_Dashboard),
   path('Host-Approvel-Process/<int:id>/',Host_Approvel_Process),
   

 


   path('Users-allPropertyCards/',User_Showing_All_Cards),              # Show Dynamically All The Cards In Web Page
   path('User-Show-All-Cards-Detail-Diff-Page/<int:id>/',User_Show_All_Details_Of_Particuler_Card),
   path('User-Search-Value/',Search_Request),
   path('User-Registration/',User_Registration),
   path('User-Login/',User_Login),
   path('User-Wishlist/', User_Wishlist),
   path('User-Wishlist-fatch/<int:id>/', User_Wishlist_Fatch),
   path('Experience/<str:pk>/',Experience),
   path('Home/<str:pk>/',Home),
   path('Services/<str:pk>/',Services),

   path('create-order/',create_razorpay_order),
   path('verify-payment/',verify_payment),
   path('User-Track-Booking/<int:id>/<str:nm>/',User_Track_Booking),
   path('User-Comments/',User_Comments),
   path('User-Read-Comments/<int:pk>/', User_Read_Comments),
   path('User-Reported-Host/',User_Reported_Host), 


   


   path('Admin-login/', Admin_login),
   path('Admin-Booking/',Admin_Booking),
   path('Admin-Users/',Admin_Users),
   path('Admin-Mange-Booking/',Admin_Mange_Booking),
   path('Admin-Mange-Users/',Admin_Mange_Users),
   path('Admin-Varified-Host/<int:pk>/',Admin_Varified_Host),
   path('Admin-Varified-Delete/<int:pk>/',Admin_Varified_Delete),
   path('Admin-Mange-Hosts/',Admin_Mange_Host),
   path("Admin-Update-Hosts-Details/<int:id>/",Admin_Update_Host_Details,),
   path('Admin-Manage-Login-History/',Admin_Manage_Login_History),
   path('Admin-Manage-Paymets/',Admin_Manage_Paymets),
   path('Admin-Approved-Swich/',Admin_Approved_Swich),
   path('Admin-Alllow/',Admin_Alllow),
   path('Admin-Manage-FeedBack/',Admin_Manage_FeedBack),
   # path('Admin-Mange-Refunds/',Admin_Mange_Refunds),

   path('admin-booking-list/', admin_booking_list),
   path('Admin-Refund-List/', admin_refund_list),
   path('update-refund-status/', update_refund_status),
   path('process-refund/', process_refund),
   path('refund-details/<int:booking_id>/', refund_details),
   # path('Admin-Fatch-All-Host-Details/',Admin_Fetch_All_Host_Details,),
   path("Admin-Fatch-All-Host-Details/", Admin_Fetch_All_Host_Details),
   path("create-payment-intent", create_payment_intent),

]


