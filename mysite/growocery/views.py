from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

from .forms import UserForm, ProfileForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect


def index(request):
    return HttpResponse("Hello, world. You're at the grocery index.")

def register(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST) 
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.refresh_from_db()
            
            profile_form = ProfileForm(request.POST, instance=user.customerprofile)
            profile_form.full_clean()
            profile_form.save()
            
            raw_password = user_form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            
            return redirect('/growocery')
    else:
        user_form = UserForm()
        profile_form = ProfileForm()
    return render(request, 'growocery/register.html', {'user_form': user_form, 'profile_form': profile_form})    