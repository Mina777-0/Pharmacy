from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name= 'core'
urlpatterns= [
    path('signup/', views.signup, name="signup"),
    path('email_verify/<uidb64>/<token>/',views.email_verification, name="email_verify"),
    path('admin_home', views.admin_home, name="admin_home"),
    path('', views.signin, name="signin"),
    path('signout', views.signout, name="signout"),
    path('groups/', views.groups, name="groups"),
    path('groups/<str:group_name>', views.group, name="group"),
    path('remove_group/<str:group_name>', views.remove_group, name="remove_group"),
    path('remove_permissions/<str:group_name>', views.remove_permissions, name="remove_permissions"),
    path('users/', views.users, name="users"),
    path('remove_user_from_group', views.remove_user_from_group, name="remove_user_from_group"),
    # Pharmacy pages urls
    path('pharmacys/', views.pharmacys, name="pharmacys"),
    path('pharmacy/update_pharmacy/<int:pharmacy_id>/', views.update_pharamcy, name="update_pharmacy"),
    path('pharmacy/remove_pharmacy/<int:pharmacy_id>/', views.remove_pharmacy, name= "remove_pharmacy"),
    path('pharmacy/pharmacy_stock/<int:pharmacy_id>/', views.pharmacy_stock, name="pharmacy_stock"),
    path('pharmacy/pharamcy_stock_update/<int:pharmacy_id>/<int:medicine_id>/', views.update_pharmacy_stock, name="update_pharmacy_stock"),
    # Doctors pages urls
    path('doctors/', views.doctors, name="doctors"),
    path('doctors/doctor/<int:doctor_id>/', views.doctor, name="doctor"),
    path('doctors/remove_doctor/<int:doctor_id>/', views.remove_doctor, name="remove_doctor"),
    # Medicines and categories urls
    path('categories/', views.categories, name="categories"),
    path('categories/category/<int:category_id>/', views.category, name="category"),
    path('categories/remove_category/<int:category_id>/', views.remove_category, name="remove_category"),
    path('medicines/', views.all_medicines, name="medicines"),
    path('medicines/edit_medicine/<int:medicine_id>/', views.edit_medicine, name="edit_medicine"),
    path('medicines/remove_medicine/<int:medicine_id>/', views.remove_medicine, name="remove_medicine"),
    # Cart and orders urls
    path('add_to_cart/<int:pharmacy_id>/<int:medicine_id>/', views.add_to_cart, name="add_to_cart"),
    path('carts/', views.carts, name="carts"),
    path('carts/user_cart/<int:user_id>/', views.cart, name="cart"),
    # Payment methods
    path('order/create_order/<int:user_id>/', views.create_order, name="create_order"),
    path('payment/<int:order_id>/', views.payment_page, name="payment"),
    path('payment/checkout_session/<int:order_id>/', views.checkout_session, name="checkout"),
    path('payment/payment_succeeded', views.success_payment, name="success_payment"),
    path('payment/payment_cancelled', views.cancel_payment, name="cancel_payment"),
    path('orders/', views.orders, name="orders"),
    
] + static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)