from django import forms

from django.contrib.auth.models import User
from .models import CustomerProfile
from django.contrib.auth.forms import UserCreationForm

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')
        
class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ('addressLine', 'postcode', 'phone', 'bsb', 'bankAccount')
        
