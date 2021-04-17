from django.contrib import admin

from .models import PostCodeCommunity, CustomerProfile, GroceryChain, DeliveryFee, GroceryStore, Item, Order, Invoice, Cart, Pickup, CommunityGroceryGroup, Price


admin.site.register(PostCodeCommunity)
admin.site.register(CustomerProfile)
admin.site.register(GroceryChain)
admin.site.register(DeliveryFee)
admin.site.register(GroceryStore)
admin.site.register(Item)
admin.site.register(Order)
admin.site.register(Invoice)
admin.site.register(Cart)
admin.site.register(Pickup)
admin.site.register(CommunityGroceryGroup)
admin.site.register(Price)

