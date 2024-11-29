from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileEditForm

@login_required
def profile(request):
    return render(request, 'mypage/profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "프로필이 성공적으로 수정되었습니다.")
            return redirect('mypage:profile')
        else:
            messages.error(request, "프로필 수정에 실패했습니다.")
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'mypage/edit_profile.html', {'form': form})