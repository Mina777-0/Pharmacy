from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authtoken.models import Token
from core.models import CustomUser, Pharmacy, PharmacyStock, Cart, Item, Order, OrderItem, Medicine
from .serialisers import SignupSerialiser, SigninSerialiser, PharmacySerialiser, StockSerialiser, CartItemsSerialser

# "102f932f978cc64db4435047bab6f6601c71a7af" Mina
# "3aa091753983979e6069c92322ba249559dbfef1" Nahid
# "32faca92b7a7cc3591e1aa9b293eb6c1661ecd44" Harry


# Sign-up page
def signup_page(request):
    return render(request, 'user/signup_page.html')

# Signup
@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def signup(request: Request):
    serialiser= SignupSerialiser(data=request.data)
    if serialiser.is_valid():
        user= serialiser.save()
        token= Token.objects.create(user=user)
        response= {
            "message": "User is created successfully",
            "data": serialiser.data,
            "token": token.key,
        } 
        return Response(data=response, status= status.HTTP_201_CREATED)
    return Response(data= serialiser.errors, status= status.HTTP_400_BAD_REQUEST)

# Email verification
'''@api_view(['GET'])
def verify_email(request: Request):
    token= request.query_params.get('token')
    if not token:
        return Response({"error": "Token is required"}, status= status.HTTP_400_BAD_REQUEST)
    
    user= get_object_or_404(CustomUser, email_verification_token= token)
    user.is_active= True
    user.email_verification_token= None
    user.save()

    return Response({"message": "User is verified successfully"}, status= status.HTTP_200_OK)'''


# Sign-in page
def signin_page(request):
    return render(request, "user/signin_page.html")

# Signin
@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([AllowAny])
def signin(request:Request):        
    serialiser= SigninSerialiser(data= request.data)
    if serialiser.is_valid():
        user= serialiser.get_user()
        token, created= Token.objects.get_or_create(user=user)
        response= {
            "message": "You have signed in",
            "data": serialiser.data,
            "token": token.key,
        }
        return Response(data= response, status= status.HTTP_200_OK)
    return Response(data= serialiser.errors, status= status.HTTP_400_BAD_REQUEST)
    

# Main page
def main_page(request):
    return render(request, "user/main_page.html")

# Main page pharamcies api
@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def main(request: Request):
    pharmacies= Pharmacy.objects.all()
    serialisers= PharmacySerialiser(instance= pharmacies, many= True)
    return Response(data= serialisers.data, status= status.HTTP_200_OK)
    
# Pharmacy page
def pharmacy_page(request):
    return render(request, "user/pharmacy_page.html")

# Get Pharmacy
@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def pharmacy_stock(request: Request, pharmacy_id):
    pharmacy= get_object_or_404(Pharmacy, pk= pharmacy_id)
    pharmacy_stock= PharmacyStock.objects.filter(pharmacy= pharmacy)

    serialiser= StockSerialiser(instance= pharmacy_stock, many= True)
    return Response(data= serialiser.data, status= status.HTTP_200_OK)


# Add to cart
@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def add_to_cart(request: Request, pharmacy_id, medicine_id):
    pharmacy= get_object_or_404(Pharmacy, id= pharmacy_id)
    medicine= get_object_or_404(Medicine, id= medicine_id)
    pharmacy_stock_item= get_object_or_404(PharmacyStock, medicine= medicine, pharmacy= pharmacy)

    cart, cart_created= Cart.objects.get_or_create(user= request.user) # Since permission class is authenticated, we can use request.user automcatically
    item, item_created= Item.objects.get_or_create(cart= cart, item= pharmacy_stock_item)

    if pharmacy_stock_item.quantity > 0:
        if item_created:
            item.quantity = 1
            pharmacy_stock_item.quantity -= 1
            item.save()
            pharmacy_stock_item.save()
            return Response({"message": "Cart is updated successfully"}, status= status.HTTP_201_CREATED)
        
        elif item:
            item.quantity += 1
            pharmacy_stock_item.quantity -= 1
            item.save()
            pharmacy_stock_item.save()
            return Response({"message": "cart is updated successfully"}, status= status.HTTP_201_CREATED)
    return Response({"error": "This item runout of the stock"}, status= status.HTTP_400_BAD_REQUEST)


# Cart page
def cart_page(request):
    return render(request, "user/cart_page.html")

# User cart 
@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def user_cart(request: Request):
    user= get_object_or_404(CustomUser, id= request.user.id)
    print(f"user: {user}")
    cart= Cart.objects.filter(user=user).first()

    if not cart:
        print("No cart found for this user")
        return Response({"error": "No cart found for this user"}, status= status.HTTP_404_NOT_FOUND)
    
    cart_items= cart.cart_items.all()
    print(f"Items: {cart_items}")
    cart_items_serialisers= CartItemsSerialser(instance= cart_items, many=True)
    return Response(data= cart_items_serialisers.data, status= status.HTTP_200_OK)