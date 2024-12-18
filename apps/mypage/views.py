from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileEditForm, CustomUserEditForm


# @login_required
# def profile_view(request):
#     """
#     사용자 프로필을 보여주는 뷰.
#     """
#     return render(request, 'mypage/profile.html', {'user': request.user})

@login_required
def profile_view(request):
    profile = request.user.profile
    return render(request, 'mypage/profile.html', {'user': request.user, 'profile': profile})

@login_required
def edit_profile_view(request):
    """
    사용자 프로필을 편집하는 뷰.
    GET 요청: 현재 사용자 정보를 폼에 표시.
    POST 요청: 폼 데이터를 검증하고 저장.
    """
    profile = request.user.profile  # Profile 인스턴스 가져오기
    user = request.user  # CustomUser 인스턴스 가져오기

    if request.method == 'POST':
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        user_form = CustomUserEditForm(request.POST, instance=user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, "프로필이 성공적으로 수정되었습니다.")
            return redirect('mypage:profile')
        else:
            messages.error(request, "프로필 수정에 실패했습니다. 모든 필드를 올바르게 입력했는지 확인하세요.")
    else:
        profile_form = ProfileEditForm(instance=profile)
        user_form = CustomUserEditForm(instance=user)

    context = {
        'profile_form': profile_form,
        'user_form': user_form,
    }
    return render(request, 'mypage/edit_profile.html', context)
