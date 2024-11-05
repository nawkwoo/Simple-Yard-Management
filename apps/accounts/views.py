# apps/accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import HttpResponse

def index(request):
    return HttpResponse("Welcome to the 어우송 YMS App")

def start(request):
    return HttpResponse("This is the start page.")

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        user_type = request.POST.get('user_type')  # Admin or Employee 선택

        if form.is_valid():
            user = form.save()
            user.profile.user_type = user_type  # Profile에 user_type 저장
            user.profile.save()
            login(request, user)
            messages.success(request, f'Account created for {user.username} as {user_type}')
            return redirect('accounts:index')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.profile.user_type == 'admin':
                messages.success(request, 'Logged in as Admin')
            else:
                messages.success(request, 'Logged in as Employee')
            return redirect('accounts:index')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('accounts:index')