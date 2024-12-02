# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile, Driver

class ProfileInline(admin.StackedInline):
    """
    Profile 모델을 CustomUserAdmin에 인라인으로 추가.
    """
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    """
    CustomUser 모델을 위한 관리자 인터페이스 설정.
    """
    model = CustomUser
    list_display = ['username', 'email', 'user_type', 'is_staff', 'is_active']
    list_filter = ['user_type', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type',)}),  # 'gender', 'birth_date', 'has_car' 제거
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('user_type',)}),  # 'gender', 'birth_date', 'has_car' 제거
    )
    search_fields = ['username', 'email']
    ordering = ['username']
    inlines = [ProfileInline]  # Profile 인라인 추가

class DriverAdmin(admin.ModelAdmin):
    """
    Driver 모델을 위한 관리자 인터페이스 설정.
    """
    list_display = ['driver_id', 'get_username']  # 'user' 대신 'get_username' 사용
    search_fields = ['driver_id', 'profile__user__username']
    
    def get_username(self, obj):
        return obj.profile.user.username
    get_username.short_description = '사용자 이름'

# 관리자 사이트에 모델 등록
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Driver, DriverAdmin)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'birth_date', 'has_car']
    search_fields = ['user__username', 'user__email']
    list_filter = ['gender', 'has_car']

admin.site.register(Profile, ProfileAdmin)