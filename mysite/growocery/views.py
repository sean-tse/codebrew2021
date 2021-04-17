from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

from .forms import UserForm, ProfileForm
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from .models import PostCodeCommunity
import datetime
from .models import PostCodeCommunity, CustomerProfile, GroceryChain, DeliveryFee, GroceryStore, Item, Order, Invoice, Cart, Pickup, CommunityGroceryGroup, Price, OrderPrice

from collections import defaultdict
import math
import json
import decimal
from django.core import serializers

def index(request):
    if request.user.is_authenticated:
        customer = CustomerProfile.objects.filter(customerAccount_id=request.user)[0]
        return redirect(f'/growocery/postcode/{customer.postcode}')
    return redirect(login_view)

def register(request):
    """
    Create a new account.
    """
    if request.user.is_authenticated:
        return redirect('/growocery/')
    else:
        if request.method == 'POST':
            user_form = UserForm(request.POST)
            profile_form = ProfileForm(request.POST)
            if user_form.is_valid() and profile_form.is_valid():
                user = user_form.save()
                user.refresh_from_db()

                profile_form = ProfileForm(request.POST, instance=user.customerprofile)
                profile_form.full_clean()
                profile_form.save()
                user.customerprofile.pcc = PostCodeCommunity.objects.get_or_create(postcode = user.customerprofile.postcode)[0]

                raw_password = user_form.cleaned_data.get('password1')
                user = authenticate(username=user.username, password=raw_password)
                login(request, user)

                return redirect('/growocery')
        else:
            user_form = UserForm()
            profile_form = ProfileForm()
        return render(request, 'growocery/register.html', {'user_form': user_form, 'profile_form': profile_form})

def login_view(request):
    """
    Login to your account.
    """
    if request.user.is_authenticated:
        return redirect('/growocery')
    else:
        if request.method == 'GET':
            return render(request, 'growocery/login.html', {'req': request})
        elif request.method == "POST":
            username = request.POST.get("username", "")
            password = request.POST.get("password", "")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("/growocery/")
            else:
                return redirect("/growocery/login/")
    pass


def logout_view(request):
    """
    Log out of your account.
    """
    if request.user.is_authenticated:
        logout(request)
        return redirect('/growocery/login/')
    else:
        return redirect('/growocery/login/')

def postcode_home(request, postcode):
    if request.user.is_authenticated:
        pcc = PostCodeCommunity.objects.get_or_create(postcode=postcode)[0]
        labels = []
        for (code, label) in GroceryChain.ChainName.choices:
            chain, boo = GroceryChain.objects.get_or_create(chain=code)
            store, boo = GroceryStore.objects.get_or_create(chain=chain, postcode=postcode, name = f"{label}  {postcode}")
            cart, boo = Cart.objects.get_or_create(store=store)
            pickup, boo =Pickup.objects.get_or_create(pickupWhen = datetime.date.today()+datetime.timedelta(days=7), store=store)
            group, boo  = CommunityGroceryGroup.objects.get_or_create(pcc=pcc, cart=cart, store=store, pickup=pickup, nextDeadline=datetime.date.today()+datetime.timedelta(days=6)) # 1 week in advance

        groups = get_list_or_404(CommunityGroceryGroup, pcc=pcc) # CommunityGroceryGroup.objects.filter(pcc=pcc)
        return render(request, 'growocery/postcode_home.html', {'groups': groups, 'postcode': postcode})
    else:
        return redirect("/growocery/login/")

def group_detail(request, id):
    if request.user.is_authenticated:
        groupStatus = 1
        if request.method == "GET":
            group = CommunityGroceryGroup.objects.filter(id=id)[0]
            myorder, boo = Order.objects.get_or_create(store=group.store, customer=request.user.customerprofile)
            return render(request, 'growocery/group_detail.html', {'group': group, 'myorder': myorder})
        elif request.method == "POST":
            pickupLocation = request.POST.get("pickupLocation", "")
            pickupWhen = request.POST.get('pickupWhen')
            group = CommunityGroceryGroup.objects.filter(id=id)[0]
            myorder, boo = Order.objects.get_or_create(store=group.store, customer=request.user.customerprofile)
            group.pickup.buyer = request.user.customerprofile
            group.pickup.locationDetails = pickupLocation
            group.pickup.pickupWhen = pickupWhen
            group.pickup.save()
            group.save()
            return render(request, 'growocery/group_detail.html', {'group': group, 'myorder': myorder})
    else:
        return redirect('/growocery/login/')

def group_catalogue(request, id):
    if request.user.is_authenticated:
        group =  get_object_or_404(CommunityGroceryGroup, id=id) # group = CommunityGroceryGroup.objects.filter(id=id)[0]
        prices = Price.objects.filter(item__chain=group.store.chain)
        myorder, boo = Order.objects.get_or_create(store=group.store, customer=request.user.customerprofile)
        pricesDict = {}
        for index, price in enumerate(prices):
            itemDict = {}
            itemDict['id'] = price.id
            itemDict['itemName'] = price.item.name
            itemDict['qty'] = price.quantity
            itemDict['price'] = str(price.price)
            itemDict['img'] = price.item.img
            pricesDict[index] = itemDict
        pricesJson = json.dumps(pricesDict)
        context = {'prices': prices, 'myorder':myorder, 'group':group, 'pricesJson': pricesJson}
        return render(request, 'growocery/group_catalogue.html', context)
    else:
        return redirect('/growocery/login/')

def group_members(request, id):
    if request.user.is_authenticated:
        group = group =  get_object_or_404(CommunityGroceryGroup, id=id)
        myorder, boo = Order.objects.get_or_create(store=group.store, customer=request.user.customerprofile)
        return render(request, 'growocery/group_members.html', {'myorder':myorder, 'group':group})
    else:
        return redirect('/growocery/login/')

# knapsack problem lol
# minimise cost
# input: total quantity
# prices for varying quantities
# solution price_id, quantity
def solve_cost(total_quant, options):
    min_cost = math.inf
    final_sol = None
    # base case: not a solution
    if total_quant < 0:
        return min_cost, final_sol
    # base case: solution found
    if total_quant == 0:
        return 0, defaultdict(int)
    for option in options:
        remainder = total_quant - option.quantity
        cost, sol = solve_cost(remainder, options)
        if sol is None:
            continue
        cost += float(option.price)
        sol[option.id] += 1
        if cost < min_cost:
            min_cost = cost
            final_sol = sol
    return min_cost, final_sol


def group_list(request, id):
    if request.user.is_authenticated:
        group =  get_object_or_404(CommunityGroceryGroup, id=id) # CommunityGroceryGroup.objects.filter(id=id)[0]
        myorder, boo = Order.objects.get_or_create(store=group.store, customer=request.user.customerprofile)
        group.cart.groupOrders.add(myorder)

        # create new combined Order
        if group.cart.combinedOrder:
            group.cart.combinedOrder.delete()
        group.cart.combinedOrder = Order.objects.create(store=group.store)

        breakdown = defaultdict(int) # key: item id, value: total quantity
        original_cost = 0
        for order in group.cart.groupOrders.all():
            for price in order.prices.all():
                original_cost += price.price
                breakdown[price.item.id] += price.quantity

        print(breakdown)
        new_cost = 0
        for item_id in breakdown.keys():
            total_quant = breakdown[item_id]
            options = get_list_or_404(Price, item__id=item_id)
            min_cost, final_sol = solve_cost(total_quant, tuple(options))
            print(f"Item name: {get_object_or_404(Item, id=item_id).name}")
            print(f"Required quantity: {total_quant}")
            for pid in final_sol.keys():
                price = get_object_or_404(Price, id=pid)
                quant = final_sol[pid]
                new_cost += price.price*quant
                print(f"Buy {price.item.name} x {price.quantity} x {quant}")
                for i in range(quant):
                    OrderPrice.objects.create(order=group.cart.combinedOrder, price=price)

        print(f"Original cost: ${original_cost}")
        print(f"New cost: ${new_cost}")
        print(f"Savings: ${original_cost - new_cost}")

        return render(request, 'growocery/group_list.html', {'group': group, 'myorder': myorder, 'original_cost':original_cost, 'new_cost': new_cost})
    else:
        return redirect('/growocery/login/')

def add_one(request, price_id, group_id, order_id):
    price = get_object_or_404(Price, id=price_id) # price = Price.objects.filter(id=price_id)[0]
    myorder = get_object_or_404(Order, id=order_id) # myorder = Order.objects.filter(id=order_id)[0]
    OrderPrice.objects.create(order=myorder, price=price)
    return redirect(f"/growocery/community/{group_id}/catalogue")


def remove_one(request, price_id, group_id, order_id):
    price = get_object_or_404(Price, id=price_id) # Price.objects.filter(id=price_id)[0]
    myorder = get_object_or_404(Order, id=order_id) # Order.objects.filter(id=order_id)[0]
    record = get_list_or_404(OrderPrice, order=myorder, price=price)[0]
    record.delete()
    return redirect(f"/growocery/community/{group_id}/catalogue")
