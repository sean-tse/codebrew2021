from .models import PostCodeCommunity, CustomerProfile, GroceryChain, DeliveryFee, GroceryStore, Item, Order, Invoice, Cart, Pickup, CommunityGroceryGroup, Price


# loads in information into the database
import pandas as pd
from django.shortcuts import render, redirect
from pathlib import Path

def load_view(request):
    path = Path(__file__).parent / "./items.csv"
    df = pd.read_csv(path)
    for index, row in df.iterrows():
        chain, created = GroceryChain.objects.get_or_create(chain=row['Code'])
        item, created = Item.objects.get_or_create(chain=chain, name = row['ItemName'], img=row['image path'])
        price, created = Price.objects.get_or_create(item=item, price=row['Price'], quantity = row['Quantity'])
    return redirect('/growocery/')
