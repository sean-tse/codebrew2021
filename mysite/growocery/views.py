from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

from .forms import UserForm, ProfileForm
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from .models import PostCodeCommunity
import datetime
from .models import PostCodeCommunity, CustomerProfile, GroceryChain, DeliveryFee, GroceryStore, Item, Order, Invoice, Cart, Pickup, CommunityGroceryGroup, Price, OrderPrice, Message

from collections import defaultdict
import math
import json
import decimal
from django.core import serializers

def index(request):
    if request.user.is_authenticated:
        customer = get_object_or_404(CustomerProfile, customerAccount_id = request.user.id) 
        return redirect(f'/growocery/postcode/{customer.postcode}/')
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

def handle_delivery(group, delivery1, delivery2): #2021-04-18T11:06 %Y-%m-%dT%H:%M
    print('hello')
    bestFee = math.inf
    bestOption = None
    if delivery1 and delivery2:
        # best delivery
        window = (delivery2 - delivery1) /datetime.timedelta(hours=1) #datetime.datetime.strptime(delivery2,'%Y-%m-%dT%H:%M') - datetime.datetime.strptime(delivery1,'%Y-%m-%dT%H:%M')
        print(str(delivery2 - delivery1))
        print(delivery2)
        print(delivery1)
        print(window)
        print(group.cart.combinedOrder.orderTotal)
        options = DeliveryFee.objects.filter(chain=group.store.chain ,minPrice__lte = group.cart.combinedOrder.orderTotal, window__lte = datetime.timedelta(hours=12))
    
        if options.count() > 0:
            for option in options.all():
                if option.fee < bestFee:
                    bestFee = option.fee
                    bestOption = option
            group.pickup.fee = bestOption
        print(bestOption)
    return bestOption
    
    
def group_detail(request, id):
    if request.user.is_authenticated:
        group = CommunityGroceryGroup.objects.filter(id=id)[0]
        print(group.cart.combinedOrder)
        myorder, boo = Order.objects.get_or_create(store=group.store, customer=request.user.customerprofile)
        groupStatus = get_group_status(group, myorder)
        if request.method == "GET":
            return render(request, 'growocery/group_detail.html', {'group': group, 'myorder': myorder, 'status': groupStatus})
        elif request.method == "POST":
            pickupLocation = request.POST.get("pickupLocation", "")
            pickupWhen = request.POST.get('pickupWhen')
            group.pickup.buyer = request.user.customerprofile
            group.pickup.locationDetails = pickupLocation
            group.pickup.pickupWhen = pickupWhen
            group.pickup.window1 = request.POST.get("startdelivery")
            group.pickup.window2 = request.POST.get("enddelivery")
            group.pickup.save()
            group.save()
            groupStatus = get_group_status(group, myorder)
            return render(request, 'growocery/group_detail.html', {'group': group, 'myorder': myorder, 'status': groupStatus})
    else:
        return redirect('/growocery/login/')

def get_group_status(group, order):
    if not group.pickup.buyer:
        return 1
    return 2

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

def group_chat(request, id):
    if request.user.is_authenticated:
        group = get_object_or_404(CommunityGroceryGroup, id=id)
        myorder, boo = Order.objects.get_or_create(store=group.store, customer=request.user.customerprofile)
        messages = Message.objects.filter(group=id).order_by('timestamp')
        if request.method == "GET":
            return render(request, 'growocery/group_chat.html', {'myorder':myorder, 'group':group, 'messages': messages})
        if request.method == "POST":
            new_message_text = request.POST.get("chat-box", "")
            new_message, created = Message.objects.get_or_create(group=group, sender=request.user.customerprofile, message=new_message_text)
            messages = Message.objects.filter(group=id).order_by('timestamp')
            return render(request, 'growocery/group_chat.html', {'myorder':myorder, 'group':group, 'messages': messages})
        
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


def invoice(order, overall_sol):
    total_principle = 0
    for price in order.prices.all():
        item_id = price.item.id
        sol = overall_sol[item_id]
        item_quant = 0
        item_cost = 0
        for pid in sol.keys():
            iprice = get_object_or_404(Price, id=pid)
            quant = sol[pid]
            item_quant += iprice.quantity*quant
            item_cost += iprice.price*quant
        unit_cost = item_cost/item_quant
        total_principle += price.quantity*unit_cost
    
    Invoice.objects.filter(order=order, customer=order.customer).delete()
    new_invoice = Invoice.objects.create(order=order, customer=order.customer, amount=total_principle)
    return new_invoice

def group_list(request, id):
    if request.user.is_authenticated:
        group =  get_object_or_404(CommunityGroceryGroup, id=id) # CommunityGroceryGroup.objects.filter(id=id)[0]
        myorder, boo = Order.objects.get_or_create(store=group.store, customer=request.user.customerprofile)
        group.cart.groupOrders.add(myorder)

        # create new combined Order
        # if group.cart.combinedOrder:
        #     group.cart.combinedOrder.delete()
        group.cart.combinedOrder = Order.objects.create(store=group.store)

        breakdown = defaultdict(int) # key: item id, value: total quantity
        original_cost = 0
        for order in group.cart.groupOrders.all():
            for price in order.prices.all():
                original_cost += price.price
                breakdown[price.item.id] += price.quantity

        print(breakdown)
        new_cost = 0
        overall_sol = {} # item_id to {price_id: quantity}
        for item_id in breakdown.keys():
            total_quant = breakdown[item_id]
            options = get_list_or_404(Price, item__id=item_id)
            min_cost, final_sol = solve_cost(total_quant, tuple(options))
            overall_sol[item_id] = final_sol
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
        group.cart.combinedOrder.orderTotal = new_cost
        print(group.cart.combinedOrder.orderTotal)
        group.cart.combinedOrder.save()
        group.cart.save()
        group.save()
        
        i = invoice(myorder, overall_sol)
        
        return render(request, 'growocery/group_list.html', {'group': group, 'myorder': myorder, 'original_cost':original_cost, 'new_cost': new_cost})
    else:
        return redirect('/growocery/login/')

def add_one(request, price_id, group_id, order_id):
    price = get_object_or_404(Price, id=price_id) # price = Price.objects.filter(id=price_id)[0]
    myorder = get_object_or_404(Order, id=order_id) # myorder = Order.objects.filter(id=order_id)[0]
    OrderPrice.objects.create(order=myorder, price=price)
    myorder.orderTotal += price.price
    myorder.save()
    return redirect(f"/growocery/community/{group_id}/catalogue")


def remove_one(request, price_id, group_id, order_id):
    price = get_object_or_404(Price, id=price_id) # Price.objects.filter(id=price_id)[0]
    myorder = get_object_or_404(Order, id=order_id) # Order.objects.filter(id=order_id)[0]
    myorder.orderTotal -= price.price
    myorder.save()
    record = get_list_or_404(OrderPrice, order=myorder, price=price)[0]
    record.delete()
    return redirect(f"/growocery/community/{group_id}/catalogue")


def confirm(request, group_id):
    if request.user.is_authenticated:
        group_list(request, group_id) # reloads grocery list
        group =  get_object_or_404(CommunityGroceryGroup, id=group_id) 
        bestOption = handle_delivery(group, group.pickup.window1, group.pickup.window2)
        myOrder = get_object_or_404(Order, customer=request.user.customerprofile, store=group.store)
        invoice = get_object_or_404(Invoice, customer=request.user.customerprofile, order=myOrder)
        myOrder.invoiceGenerated = True
        myOrder.save()
        og_total = myOrder.orderTotal
        savings = myOrder.orderTotal - invoice.amount
        new_total = invoice.amount
        if bestOption:
            new_total += bestOption.fee / group.cart.groupOrders.count() 
            og_total += bestOption.fee 
            savings += bestOption.fee - bestOption.fee / group.cart.groupOrders.count() 
        return render(request, 'growocery/confirmation.html', context={'group': group, 'bestOption':bestOption, 'invoice': invoice, 'myorder':myOrder, 'savings': savings, 'og_total':og_total, 'new_total':new_total})
    return redirect('/growocery/login/')
