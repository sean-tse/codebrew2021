from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator

# Create your models here.

class CustomerProfile(models.Model):
    customerAccount = models.OneToOneField(User, on_delete=models.CASCADE)
    addressLine = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=4, validators=[RegexValidator(r'^\d{1,10}$')], blank=True)
    phone = models.CharField(max_length=10, validators=[RegexValidator(r'^\d{1,10}$')], blank=True)
    bsb = models.CharField(max_length=6, validators=[RegexValidator(r'^\d{1,10}$')], blank=True)
    bankAccount = models.CharField(max_length=15, validators=[RegexValidator(r'^\d{1,10}$')], blank=True)
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        CustomerProfile.objects.create(customerAccount=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.customerprofile.save()    