from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.mail import EmailMessage
from django.conf import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password, **extra_fields):
        if not email:
            raise ValueError("Email Address should be provided")
        email= self.normalize_email(email)
        user= self.model(email= email, first_name= first_name, last_name= last_name, **extra_fields)
        user.set_password(password)
        user.save(using= self._db)
        return user 

    def create_superuser(self, email, first_name, last_name, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("superuser is_staff should be true")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("superuser is_superuser should be true")
        
        return self.create_user(email, first_name, last_name, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email= models.EmailField(unique= True, max_length= 255, verbose_name= "Email Address")
    first_name= models.CharField(max_length= 62)
    last_name= models.CharField(max_length= 62)
    is_active= models.BooleanField(default= False)
    is_staff= models.BooleanField(default= False)
    date_joined= models.DateTimeField(default= timezone.now)
    last_login= models.DateTimeField(blank= True, null= True)
    email_verified= models.BooleanField(default= False)
    

    objects= CustomUserManager()

    USERNAME_FIELD= 'email'
    REQUIRED_FIELDS= ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def activate(self):
        self.is_active = True
        self.save()

    def deactivate(self):
        self.is_active= False
        self.save()



    

# Pharmacy Model
class Pharmacy(models.Model):
    name= models.CharField(max_length= 255, unique= True)
    address= models.CharField(max_length=255)
    phone_regex= RegexValidator(r'^\+\d{9,15}$', message="The phone number format must be +111 555 666 777")
    phone_number= models.CharField(validators=[phone_regex], max_length= 16)
    email= models.EmailField(unique= True)

    class Meta:
        indexes= [
            models.Index(fields=["name"])
        ]

        constraints= [
            models.UniqueConstraint(fields=["name", "address"], name= "unique_pharmacy_name_address")
        ]

    def __str__(self):
        return f"{self.name} - {self.address}"
    
    def average_review(self):
        ratings= self.ratings.all()

        if ratings.exists():
            return sum(rating.stars for rating in ratings)/ratings.count()
        return 0
    
    def review_count(self):
        return self.reviews.count()


# Phrmacy review
class Review(models.Model):
    customer= models.OneToOneField(settings.AUTH_USER_MODEL, on_delete= models.CASCADE)
    pharmacy= models.ForeignKey(Pharmacy, related_name="reviews", on_delete= models.CASCADE)
    contents= models.TextField()
    time_stamp= models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return f"{self.customer} reviewed {self.pharmacy} at {self.time_stamp}"

# Rating
class Rating(models.Model):
    customer= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE)
    pharmacy= models.ForeignKey(Pharmacy, on_delete= models.CASCADE, related_name="ratings")
    stars= models.PositiveIntegerField()
    time_stamp= models.DateTimeField(auto_now= True)

    class Meta:
        indexes= [
            models.Index(fields=["customer"]),
            models.Index(fields=["pharmacy"])
        ]
        
        constraints= [
            models.UniqueConstraint(fields=["customer", "pharmacy"], name= "unique_customer_pharmacy_rating")
        ]

    def __str__(self):
        return f"{self.customer} rated {self.pharmacy} {self.stars} stars at {self.time_stamp}"
    
    def save(self, *args, **kwargs):
        if not (1 < self.stars < 5):
            raise ValueError("Rating must to be between 1 and 5")
        super(Rating, self).save(*args, **kwargs)


# Doctors Model
class Doctor(models.Model):
    class Shift(models.TextChoices):
        Morning= "AM", "AM"
        Evening= "PM", "PM"
    
    class Days(models.TextChoices):
        Mon= "Monday", "Monday"
        Tue= "Tuesday", "Tuesday"
        Wed= "Wednesday", "Wednesday"
        Thu= "Thursday", "Thursday"
        Fri= "Friday", "Friday"
        Sat= "Saturday", "Saturday"
        Sun= "Sunday", "Sunday"

    # File directory doctors images
    def doctors_directory_path(instance, filename):
        return f"doctors/{instance.first_name}/{instance.last_name}/{timezone.now().strftime("%Y/%m/%d")}/{filename}"

    
    first_name= models.CharField(max_length=64)
    last_name= models.CharField(max_length= 64)
    photo= models.ImageField(null= True, blank= True, upload_to= doctors_directory_path)
    pharmacy= models.ManyToManyField(Pharmacy, related_name="doctors")
    is_active= models.BooleanField(default= True)
    shift= models.CharField(max_length=10, choices= Shift.choices)
    days= models.CharField(max_length=100)

    class Meta:
        indexes=[
            models.Index(fields=["first_name"]),
            models.Index(fields= ["last_name"])
        ]
        
        constraints=[
            models.UniqueConstraint(fields=["first_name", "last_name"], name= "unique_doctor_name")
        ]
    
    # Getting the shift filed
    def get_shift(self):
        return self.shift
    
    # Setting the shift field
    def set_shift(self, shift):
        if shift in self.Shift.values:
            self.shift= shift
        else:
            raise ValueError("Invalid shift choice")
    
    # Getting the days
    def get_days(self):
        return self.days.split(",")
    
    # Setting the days
    def set_days(self, days):
        for day in days:
            if day not in self.Days.values:
                return ValueError("Invalid day choice")
            
        self.days= ",".join(days)


    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name}"
    
    def activate(self):
        self.is_active= True
        self.save()

    def deactivate(self):
        self.is_active= False
        self.save()


# Medicine Categories
class Category(models.Model):
    name= models.CharField(max_length=64, unique= True)

    def __str__(self):
        return self.name


# Functions regarding Medicine class
import random
import string

def generate_serial_number(instance):
        # instance here to access the model's fields by passing the model instance itself
        sss= "".join(random.choices(string.digits, k= 3))
        return f"{sss}--{instance.category.id}--{instance.name}--{instance.production_date.year}"


# Medicine
class Medicine(models.Model):

    def medicine_directory_path(instance, filename):
        return f"medicine/{instance.category.name}/{instance.name}/{timezone.now().strftime('%Y/%m/%d')}/{filename}"
    

    name= models.CharField(max_length=255, unique= True)
    leaflet= models.TextField()
    category= models.ForeignKey(Category, related_name="medicines", on_delete= models.CASCADE)
    production_date= models.DateField()
    expiry_date= models.DateField()
    company= models.CharField(max_length=255)
    image= models.ImageField(null= True, blank= True, upload_to=medicine_directory_path)
    price= models.DecimalField(max_digits= 10, decimal_places= 2)
    serial_number= models.CharField(
        max_length=255, 
        unique= True,
        editable= False,
        validators=[
            RegexValidator(
                regex=r"^[0-9]{3}--\d+--.+--\d{4}$",
                message="Serial number must be in the format sss--categoryID--Name--YYYY",
                code="Invalid serial number",
            )
        ]
        )

    class Meta:
        indexes= [
            models.Index(fields=["name"]),
            models.Index(fields=["category"]),
            models.Index(fields=["company"])
        ]
        
        constraints=[
            models.UniqueConstraint(fields=["name", "category", "company"], name="unique_name_cat_comp")
        ]

    def __str__(self):
        return f"{self.name} - {self.category}"
    

    def save(self, *args, **kwargs):
        if not self.serial_number:
            self.serial_number= generate_serial_number(self)
        super(Medicine, self).save(*args, **kwargs)
    


# Pharmacies stocks model
class PharmacyStock(models.Model):
    medicine= models.ForeignKey(Medicine, on_delete= models.CASCADE, related_name="items")
    pharmacy= models.ForeignKey(Pharmacy, on_delete= models.CASCADE, related_name="stock")
    in_stock= models.BooleanField(default= True)
    quantity= models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.pk:
            # Shortage in stock
            if self.quantity == 10:
                subject= "Item shortage reminder"
                message= f"Item {self.medicine.name} is running short in your stock"

                email= EmailMessage(subject, message, from_email= settings.EMAIL_HOST_USER, to=[self.pharmacy.email])
                email.send(fail_silently= False)

            # Out of stock
            if self.quantity == 0:
                subject= "Item shortage reminder"
                message= f"{self.medicine.name} is out of your stock"

                email= EmailMessage(subject, message, from_email= settings.EMAIL_HOST_USER, to=[self.pharmacy.email])
                email.send(fail_silently= False)

                self.in_stock= False
        super(PharmacyStock,self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.medicine.name} at {self.pharmacy.name}"

'''
    In case of many-to-many relationship, you need to determine the phrmacy first and then send the email.

    pharmacies= self.pharmacy.all()

    for pharmacy in pharmacies:
        email= EmailMessage(subject, message, from_email= settings.EMAIL_HOST_USER, to=[pharmacy.email])
'''



# Cart model
class Cart(models.Model):
    user= models.OneToOneField(settings.AUTH_USER_MODEL, on_delete= models.CASCADE, related_name="cart")

    def __str__(self):
        return f"{self.user.first_name}'s cart"
    
    # Total quantity
    def total_quantity(self):
        return self.cart_items.count()
    
    # Total cost
    def total_cost(self):
        total= sum(item.subtotal() for item in self.cart_items.all())
        return total
    

# Cart items
class Item(models.Model):
    item= models.ForeignKey(PharmacyStock, on_delete= models.CASCADE)
    cart= models.ForeignKey(Cart, on_delete= models.CASCADE, related_name= "cart_items")
    quantity= models.PositiveIntegerField(default=0)
    created= models.DateTimeField(auto_now_add= True)


    def subtotal(self):
        return self.quantity * self.item.medicine.price
    
    def save(self, *args, **kwargs):
        if self.pk:
            days_difference= (timezone.now() - self.created).days
            if days_difference > 15:
                self.delete()
                return 
            
            pharmacy_stock_items= self.item.pharmacy.stock.all()
            for pharmacy_stock_item in pharmacy_stock_items:
                if pharmacy_stock_item.quantity <= 5:
                    if days_difference == 4:
                        subject= "Item removal from cart reminder"
                        message= "Dear customer, due to certain circumstances, you have 24 hours to confirm your order for this item"
                        email= EmailMessage(subject, message, from_email= settings.EMAIL_HOST_USER, to=[self.cart.user.email])
                        email.send(fail_silently= False)

                    if days_difference == 3:
                        self.delete()
                        return
                
        super(Item, self).save(*args, **kwargs)


# Order model
class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING= "P", "Pending"
        DELIVERED= "D", "Delivered"
        CANCELLED= "C", "Cancelled"
    
    class PaymentMethod(models.TextChoices):
        CARD= "Card", "Card"
        CASH= "Cash", "Cash"
    
    user= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE, related_name= "user_orders")
    created_date= models.DateTimeField(auto_now_add= True)
    updated_date= models.DateTimeField(auto_now= True)
    payment_method= models.CharField(max_length=4, choices= PaymentMethod.choices)
    paid= models.BooleanField(default= False)
    purchase_amount= models.DecimalField(max_digits=10, decimal_places=2, editable= False)
    status= models.CharField(max_length=2, choices= OrderStatus.choices, default= OrderStatus.PENDING)


    def __str__(self):
        return f"Order number {self.pk} at {self.created_date}"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            cart_items= self.user.cart.cart_items.all()
            self.purchase_amount= sum(item.item.medicine.price * item.quantity for item in cart_items)

        else:
            if self.paid == True:
                subject= "Order status update"
                message= "Dear Customer, your order is paid. Thanks"
                email= EmailMessage(subject, message, from_email= settings.EMAIL_HOST_USER, to=[self.user.email])
                email.send(fail_silently=False)

            if self.status == "CANCELLED":
                subject= "Order status update"
                message= "Dear Customer, your order is cancelled. Please, reach out for more information"
                email= EmailMessage(subject, message, from_email= settings.EMAIL_HOST_USER, to=[self.user.email])
                email.send(fail_silently=False)

        
        super(Order, self).save(*args, **kwargs)


# Order items
class OrderItem(models.Model):
    order= models.ForeignKey(Order, related_name="order_items", on_delete= models.CASCADE)
    item= models.ForeignKey(PharmacyStock, on_delete= models.CASCADE)
    quantity= models.PositiveIntegerField(default= 1)
    price= models.DecimalField(decimal_places=2, max_digits=10, editable=False)

    def __str__(self):
        return f"{self.quantity} x {self.item.medicine.name} from {self.item.pharmacy.name} in the order (Order #{self.order.pk})"

    