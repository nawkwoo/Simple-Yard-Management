from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import AdminSignUpForm, StaffSignUpForm
from django.contrib import messages

def signup(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type', 'admin')
        if user_type not in ['admin', 'staff']:
            user_type = 'admin'
        form_class = AdminSignUpForm if user_type == 'admin' else StaffSignUpForm
        form = form_class(request.POST)
        
        if form.is_valid():
            user = form.save()
            messages.success(request, "회원가입이 완료되었습니다. 로그인 창으로 이동합니다.")
            return redirect('accounts:login')
        else:
            print(form.errors)
            messages.error(request, "회원가입에 실패했습니다. 입력 내용을 확인해주세요.")
    else:
        user_type = request.GET.get('user_type', 'admin')
        form_class = AdminSignUpForm if user_type == 'admin' else StaffSignUpForm
        form = form_class()

    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, '사용자 이름과 비밀번호를 모두 입력해주세요.')
            return render(request, 'accounts/login.html')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "로그인에 성공했습니다.")
            next_url = request.GET.get('next', 'dashboard:home')
            return redirect(next_url)
        else:
            messages.error(request, '로그인에 실패하였습니다. 다시 시도해주세요.')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, '로그아웃 되었습니다.')
    return redirect(request.META.get('HTTP_REFERER', 'accounts:login'))