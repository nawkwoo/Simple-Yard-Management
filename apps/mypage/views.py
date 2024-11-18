from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileEditForm

@login_required
def profile(request):
    # 현재 로그인된 사용자 정보를 템플릿에 전달
    return render(request, 'mypage/profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "프로필이 성공적으로 수정되었습니다.")
            return redirect('mypage:profile')
    else:
        form = ProfileEditForm(instance=request.user)  # 기존 정보로 폼 초기화

    return render(request, 'mypage/edit_profile.html', {'form': form})