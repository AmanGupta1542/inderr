from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

from .forms import UserLogin

# Create your views here.

def index(request):
    if request.user.is_authenticated:
        return render(request, 'inderr/dashboard.html')
    else:
        return redirect('/login')


def change_password(request):
    if request.user.is_authenticated:
        return render(request, 'inderr/change-password.html')
    else:
        return redirect('/login')

def user_login(request):
    # if request.user.is_authenticated:
    #     return redirect("/")
    if request.user.is_authenticated:
        return redirect('/')
    else :
        if request.method == "POST":
            form = UserLogin(request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.info(request, f"You are now logged in as {username}.")
                    return redirect("/")
                else:
                    messages.error(request,"Invalid username or password.")
            else:
                messages.error(request,"Invalid username or password.")
        form = UserLogin()
        return render(request=request, template_name="inderr/login.html", context={"login_form":form})


def user_logout(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("/login")