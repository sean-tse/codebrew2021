from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator
from django.utils.translation import gettext as _

# Create your models here.


class PostCodeCommunity(models.Model):
    postcode = models.CharField(max_length=4, validators=[RegexValidator(r'^\d{1,10}$')], blank=True)


class CustomerProfile(models.Model):
    customerAccount = models.OneToOneField(User, on_delete=models.CASCADE)
    addressLine = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=4, validators=[RegexValidator(r'^\d{1,10}$')], blank=True)
    phone = models.CharField(max_length=10, validators=[RegexValidator(r'^\d{1,10}$')], blank=True)
    bsb = models.CharField(max_length=6, validators=[RegexValidator(r'^\d{1,10}$')], blank=True)
    bankAccount = models.CharField(max_length=15, validators=[RegexValidator(r'^\d{1,10}$')], blank=True)
    pcc = models.ForeignKey(PostCodeCommunity, on_delete=models.CASCADE, blank=True, null=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        CustomerProfile.objects.create(customerAccount=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.customerprofile.save()


class GroceryChain(models.Model):
    class ChainName(models.TextChoices):
        COLES = 'COL', _('Coles')
        WOOLWORTHS = 'WOO', _('Woolworths')
        IGA = 'IGA', _('IGA')
        ALDI = 'ALD', _('ALDI')

    chain = models.CharField(max_length=3, choices=ChainName.choices)
    # label = "Coles"

class DeliveryFee(models.Model):
    chain = models.ForeignKey(GroceryChain, on_delete=models.CASCADE)
    minPrice = models.DecimalField(decimal_places=2, max_digits=15)
    fee = models.DecimalField(decimal_places=2, max_digits=15)

class GroceryStore(models.Model):
    chain = models.ForeignKey(GroceryChain, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    postcode = models.CharField(max_length=4, validators=[RegexValidator(r'^\d{1,10}$')], blank=True)

class Item(models.Model):
    chain = models.ForeignKey(GroceryChain, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    img = models.CharField(max_length=50)
    
class OrderPrice(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    price = models.ForeignKey('Price', on_delete=models.CASCADE)
    count = models.IntegerField(blank=True, null=True)

class Price(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2, max_digits=15)
    quantity = models.IntegerField()

    
class Order(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, blank=True, null=True)
    store = models.ForeignKey(GroceryStore, on_delete=models.CASCADE, blank=True, null=True)
    prices = models.ManyToManyField(Price, through=OrderPrice)
    orderTotal =  models.DecimalField(decimal_places=2, max_digits=15, default=0)
    invoiceGenerated = models.BooleanField(default=False)




class Invoice(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    amount =  models.DecimalField(decimal_places=2, max_digits=15)

class Cart(models.Model):
    store = models.ForeignKey(GroceryStore, on_delete=models.CASCADE, blank=True, null=True)
    combinedOrder = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='combinedOrder', blank=True, null=True)
    groupOrders = models.ManyToManyField(Order, related_name='groupOrders', blank=True, null=True)
    total = models.DecimalField(decimal_places=2, max_digits=15, blank=True, null=True)
    orderedStatus = models.BooleanField(default=False)
    orderDate = models.DateTimeField(blank=True, null=True)


class Pickup(models.Model):
    buyer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, blank=True, null=True)
    locationDetails = models.CharField(max_length=300, blank=True, null=True, default="not organised yet")
    pickupWhen = models.DateTimeField(blank=True, null=True)
    store = models.ForeignKey(GroceryStore, on_delete=models.CASCADE,blank=True, null=True)



class CommunityGroceryGroup(models.Model):
    pcc = models.ForeignKey(PostCodeCommunity, on_delete=models.CASCADE)
    nextDeadline = models.DateTimeField()
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    store = models.ForeignKey(GroceryStore, on_delete=models.CASCADE)
    pickup = models.ForeignKey(Pickup, on_delete=models.CASCADE, blank=True, null=True, related_name='pickup')
    volunteers = models.ManyToManyField(Pickup, blank=True, related_name='volunteers')
