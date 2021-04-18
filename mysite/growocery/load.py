from .models import PostCodeCommunity, CustomerProfile, GroceryChain, DeliveryFee, GroceryStore, Item, Order, Invoice, Cart, Pickup, CommunityGroceryGroup, Price


# loads in information into the database
import pandas as pd
from django.shortcuts import render, redirect
from pathlib import Path
import datetime

def load_view(request):
    # loads products
    path = Path(__file__).parent / "./items.csv"
    df = pd.read_csv(path)
    for index, row in df.iterrows():
        chain, created = GroceryChain.objects.get_or_create(chain=row['Code'])
        item, created = Item.objects.get_or_create(chain=chain, name = row['ItemName'], img=row['image path'])
        price, created = Price.objects.get_or_create(item=item, price=row['Price'], quantity = row['Quantity'])
        
    # load delivery fees
    coles, boo = GroceryChain.objects.get_or_create(chain='COL')
    woolworths, boo = GroceryChain.objects.get_or_create(chain='WOO')
    
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=coles, fee=0, minPrice=250, window=datetime.timedelta(hours=2))
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=coles, fee=0, minPrice=250, window=datetime.timedelta(hours=4))
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=coles, fee=0, minPrice=250, window=datetime.timedelta(hours=6))
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=coles, fee=11, minPrice=50, window=datetime.timedelta(hours=2))
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=coles, fee=8, minPrice=50, window=datetime.timedelta(hours=4))
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=coles, fee=4, minPrice=50, window=datetime.timedelta(hours=6))
    
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=woolworths, fee=0, minPrice=300, window=datetime.timedelta(hours=1))
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=woolworths, fee=0, minPrice=300, window=datetime.timedelta(hours=3))
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=woolworths, fee=0, minPrice=300, window=datetime.timedelta(hours=5))
    
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=woolworths, fee=9, minPrice=250, window=datetime.timedelta(hours=1))
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=woolworths, fee=3, minPrice=250, window=datetime.timedelta(hours=3))
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=woolworths, fee=1, minPrice=250, window=datetime.timedelta(hours=5))
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=woolworths, fee=11, minPrice=200, window=datetime.timedelta(hours=1))
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=woolworths, fee=6, minPrice=200, window=datetime.timedelta(hours=3))
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=woolworths, fee=4, minPrice=200, window=datetime.timedelta(hours=5))
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=woolworths, fee=13, minPrice=150, window=datetime.timedelta(hours=1))
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=woolworths, fee=9, minPrice=150, window=datetime.timedelta(hours=3))
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=woolworths, fee=7, minPrice=150, window=datetime.timedelta(hours=5))
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=woolworths, fee=15, minPrice=100, window=datetime.timedelta(hours=1))
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=woolworths, fee=12, minPrice=100, window=datetime.timedelta(hours=3))
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=woolworths, fee=10, minPrice=100, window=datetime.timedelta(hours=5))
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=woolworths, fee=17, minPrice=50, window=datetime.timedelta(hours=1))
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=woolworths, fee=15, minPrice=50, window=datetime.timedelta(hours=3))
    deliveryfee, created = DeliveryFee.objects.get_or_create(chain=woolworths, fee=13, minPrice=50, window=datetime.timedelta(hours=5))
    
    return redirect('/growocery/')
