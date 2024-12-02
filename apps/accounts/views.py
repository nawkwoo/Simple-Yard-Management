# accounts/views.py

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import AdminSignUpForm, StaffSignUpForm


def signup(request):
    """
    회원가입 뷰. user_type에 따라 관리자 또는 직원 회원가입 폼을 사용합니다.
    """
    if request.method == 'POST':
        user_type = request.POST.get('user_type', 'admin')
        form_class = AdminSignUpForm if user_type == 'admin' else StaffSignUpForm
        form = form_class(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "회원가입이 완료되었습니다. 로그인 창으로 이동합니다.")
            return redirect('accounts:login')
        else:
            messages.error(request, "회원가입에 실패했습니다. 입력 내용을 확인해주세요.")
    else:
        user_type = request.GET.get('user_type', 'admin')
        form_class = AdminSignUpForm if user_type == 'admin' else StaffSignUpForm
        form = form_class()

    context = {'form': form}
    return render(request, 'accounts/signup.html', context)


def login_view(request):
    """
    로그인 처리 뷰. 인증 성공 시 다음 URL로 리디렉션.
    """
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
    """
    로그아웃 처리 뷰.
    """
    logout(request)
    messages.success(request, '로그아웃 되었습니다.')
    return redirect('accounts:login')


@login_required
def home(request):
    """
    로그인 후 보여지는 홈 페이지 뷰. 다른 앱의 주요 URL을 컨텍스트로 전달합니다.
    """
    context = {
        'edit_url': reverse('yms_edit:equipment-list'),
        'manage_url': reverse('yms_view:view_page'),
        'order_url': reverse('dashboard:order_list'),
    }
    return render(request, 'dashboard/home.html', context)


def index(request):
    """
    기본 인덱스 뷰. 로그인 페이지로 리디렉션.
    """
    return render(request, 'accounts/login.html')
