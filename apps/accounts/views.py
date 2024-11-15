from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import AdminSignUpForm, StaffSignUpForm
from django.contrib import messages

def signup(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type', 'admin')
        form_class = AdminSignUpForm if user_type == 'admin' else StaffSignUpForm
        form = form_class(request.POST)
        
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = user_type
            user.save()
            messages.success(request, "회원가입이 완료되었습니다. 로그인 창으로 이동합니다.")
            return redirect('accounts:login')
    else:
        form = AdminSignUpForm()

    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, "로그인에 성공했습니다.")
            return redirect('dashboard:home')
        else:
            messages.error(request, '로그인에 실패하였습니다. 다시 시도해주세요.')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, '로그아웃 되었습니다.')
    return redirect('dashboard:index')