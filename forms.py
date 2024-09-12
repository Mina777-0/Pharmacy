from .models import CustomUser
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import Pharmacy, Doctor, Medicine, Category, PharmacyStock


class CustomCreationForm(forms.ModelForm):
    password1= forms.CharField(label= "Password", widget= forms.PasswordInput())
    password2= forms.CharField(label= "Confirm Password", widget= forms.PasswordInput())

    class Meta:
        model= CustomUser
        fields= ["email", "first_name", "last_name"]

    def __init__(self, *args, **kwargs):
        super(CustomCreationForm, self).__init__(*args, **kwargs)
        self.fields["email"].widget.attrs["placeholder"]= "Email Address"
        self.fields["first_name"].widget.attrs["placeholder"]= "First Name"
        self.fields["last_name"].widget.attrs["placeholder"]= "Last Name"
        self.fields["password1"].widget.attrs["placeholder"]= "Password"
        self.fields["password2"].widget.attrs["placeholder"]= "Confirm Password"

    def clean_password(self):
        password1= self.cleaned_data.get('password1')
        password2= self.cleaned_data.get('password2')

        if len(password1) < 8:
            raise forms.ValidationError("Password should at least be 8 chracters")
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        
        return password2
    
    def save(self, commit= True):
        user= super().save(commit= False)
        user.set_password(self.cleaned_data.get('password2'))

        if commit:
            user.save()
        return user
        
class CustomChangeForm(forms.ModelForm):
    password= ReadOnlyPasswordHashField()

    class Meta:
        model= CustomUser
        fields= ["email", "first_name", "last_name", "password", "is_active", "is_staff"]
    
    def clean_password(self):
        return self.initial['password']
    

class RegisterForm(CustomCreationForm):
    class Meta(CustomCreationForm.Meta):
        fields= ["email", "first_name", "last_name", "password1", "password2"]


class PharmacyRegistration(forms.ModelForm):
    class Meta:
        model= Pharmacy
        fields= "__all__"

class DoctorRegistration(forms.ModelForm):
    first_name= forms.CharField(label="First name", required=True, widget=forms.TextInput(attrs={'placeholder': "First name"}))
    last_name= forms.CharField(label= "Last name", required= True, widget=forms.TextInput(attrs={"placeholder": "Last name"}))
    photo= forms.ImageField(label="Image", required= False)
    pharmacy= forms.ModelMultipleChoiceField(
        label= "pharmacies", 
        queryset= Pharmacy.objects.all(),
        widget= forms.CheckboxSelectMultiple,
        required= True
        )
    is_active= forms.BooleanField(initial= False, required= True, label="currently active")
    shift= forms.ChoiceField(widget= forms.RadioSelect, choices= Doctor.Shift.choices)
    days= forms.CharField(label= "Days", widget=forms.TextInput(attrs={"placeholder": "Days"}))

    class Meta:
        model= Doctor
        fields= ["first_name", "last_name", "photo", "pharmacy", "is_active", "shift", "days"]

class MedicineRegistration(forms.ModelForm):
    name= forms.CharField(widget= forms.TextInput(attrs= {"placeholder": "Medicine name"}), required=True)
    leaflet= forms.CharField(widget= forms.Textarea(attrs={"placeholder":"Prescription..."}), required= True)
    category= forms.ModelChoiceField(
        queryset= Category.objects.all(),
        widget=forms.Select,
        label= "Category",
        required= True,
    )
    production_date= forms.DateField(widget=forms.DateInput(attrs={
        "type": "date",
        "placeholder": "Select a date",
    }))
    expiry_date= forms.DateField(widget= forms.DateInput(attrs={
        "type": "date",
        "placeholder": "select a date",
    }))
    company= forms.CharField(widget= forms.TextInput(attrs={"placeholder": "Company name"}))
    image= forms.ImageField()
    price= forms.DecimalField(widget= forms.NumberInput(attrs={
        "placeholder": "Enter price",
        "step": "0.01",
        "min": "0",
    }))

    class Meta:
        model= Medicine
        fields= ["name", "leaflet", "category", "production_date", "expiry_date", "company", "image", "price"]
        exclude= ["serial_number"]


class PharmacyMedicineStock(forms.ModelForm):
    medicine= forms.ModelChoiceField(
        queryset= Medicine.objects.all(),
        widget= forms.Select,
        required=True
    )
    in_stock= forms.BooleanField(initial=False, label="In stock", required=True)
    quantity= forms.IntegerField(label= "Quantity", required=True)

    class Meta:
        model= PharmacyStock
        fields=["medicine", "in_stock", "quantity"]
