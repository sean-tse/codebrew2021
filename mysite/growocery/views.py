from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

from .forms import UserForm, ProfileForm
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from .models import PostCodeCommunity

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