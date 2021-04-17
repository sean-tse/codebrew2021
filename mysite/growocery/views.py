from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

from .forms import UserForm, ProfileForm
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from .models import PostCodeCommunity
import datetime
from .models import PostCodeCommunity, CustomerProfile, GroceryChain, DeliveryFee, GroceryStore, Item, Order, Invoice, Cart, Pickup, CommunityGroceryGroup, Price


def index(request):
    return HttpResponse("Hello, world. You're at the grocery index.")

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
            chain = GroceryChain.objects.get_or_create(chain=code)[0]
            store = GroceryStore.objects.get_or_create(chain=chain, postcode=postcode, name = f"{label}  {postcode}")[0]
            cart = Cart.objects.get_or_create(store=store)[0]
            pickup=Pickup.objects.get_or_create(pickupWhen = datetime.date.today()+datetime.timedelta(days=7), store=store)[0]
            group = CommunityGroceryGroup.objects.get_or_create(pcc=pcc, cart=cart, store=store, pickup=pickup, nextDeadline=datetime.date.today()+datetime.timedelta(days=6)) # 1 week in advance

        groups = CommunityGroceryGroup.objects.filter(pcc=pcc)
        return render(request, 'growocery/postcode_home.html', {'groups': groups})
    else:
        return redirect("/growocery/login/")



def group_detail(request, id):
    if request.user.is_authenticated:
        if request.method == "GET":
            group = CommunityGroceryGroup.objects.filter(id=id)[0]
            return render(request, 'growocery/group_detail.html', {'group': group})
        elif request.method == "POST":
            group = CommunityGroceryGroup.objects.filter(id=id)[0]
            group.pickup.buyer = request.user.customerprofile
            return render(request, 'growocery/group_detail.html', {'group': group})
    else:
        return redirect('/growocery/login/')

def group_catalogue(request, id):
    if request.user.is_authenticated:
        group = CommunityGroceryGroup.objects.filter(id=id)[0]
        prices = Price.objects.filter(item__chain=group.store.chain)

        myorder = Order.objects.get_or_create(store=group.store, customer=request.user.customerprofile)[0]
        return render(request, 'growocery/group_catalogue.html', {'prices': prices, 'myorder':myorder})
    else:
        return redirect('/growocery/login/')

def group_list(request, id):
    if request.user.is_authenticated:
        group = CommunityGroceryGroup.objects.filter(id=id)[0]

        myorder = Order.objects.get_or_create(store=group.store, customer=request.user.customerprofile)[0]
        return render(request, 'growocery/group_list.html', {'group': group, 'myorder': myorder})
    else:
        return redirect('/growocery/login/')
