from core.models import CustomUser, Pharmacy, PharmacyStock, Cart, Item, Order, OrderItem, Medicine
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
import uuid
from django.core.mail import EmailMessage
from django.conf import settings



# Signup serialiser
class SignupSerialiser(serializers.ModelSerializer):
    password1= serializers.CharField(write_only= True, min_length= 8)
    password2= serializers.CharField(write_only= True, min_length= 8)

    class Meta:
        model= CustomUser
        fields= ["first_name", "last_name", "email", "password1", "password2"]

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError("Passwords don't match")
        
        if len(data["password1"]) < 8:
            raise serializers.ValidationError("Password should be at least 8 characters")
        
        return data
    
    def save(self, **kwargs):
        user= CustomUser(
            first_name= self.validated_data["first_name"],
            last_name= self.validated_data["last_name"],
            email= self.validated_data["email"],
        )
        user.set_password(self.validated_data['password2'])
        user.save()

        # User virification token
        '''
        token= uuid.uuid4().hex
        user.email_verification_token= token
        user.save()

        verification_link= f"{settings.FRONTEND_URL}/verify_email/?token={token}"
        subject= "Email verification"
        message= f"Click the following link to verify your email: {verification_link}"

        email= EmailMessage(subject, message, from_email= settings.EMAIL_HOST_USER, to=[user.email])
        email.send(fail_silently=False)'''

        return user
    

# Signin serialiser
class SigninSerialiser(serializers.Serializer):
    email= serializers.EmailField()
    password= serializers.CharField(write_only= True)

    def validate(self, data):
        user= authenticate(email= data["email"], password= data["password"])
        if user is None:
            raise serializers.ValidationError("Invalid credentials")
        self.user= user
        return data

    def get_user(self):
        return getattr(self, "user", None)



# Pharmacy serialiser
class PharmacySerialiser(serializers.ModelSerializer):
    class Meta:
        model= Pharmacy
        fields= "__all__"

# Medicine serialiser
class MedicineSerialiser(serializers.ModelSerializer):
    class Meta:
        model= Medicine
        exclude= ["category", "serial_number"]

# Pharmacy_stock serialiser
class StockSerialiser(serializers.ModelSerializer):
    medicine= MedicineSerialiser(read_only= True)
    class Meta:
        model= PharmacyStock
        fields= ["medicine"]


# Cart serialiser
class CartSerialiser(serializers.ModelSerializer):
    class Meta:
        model= Cart
        fields= "__all__"

# Cart items serialiser
class CartItemsSerialser(serializers.ModelSerializer):
    item= StockSerialiser(read_only= True)
    subtotal= serializers.SerializerMethodField()
    
    class Meta:
        model= Item
        fields= ["item", "quantity", "subtotal"]

    def get_subtotal(self, obj):
        return obj.subtotal()

    