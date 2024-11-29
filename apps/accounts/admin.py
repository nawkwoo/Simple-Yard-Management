# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from .models import CustomUser

# class CustomUserAdmin(UserAdmin):
#     model = CustomUser
#     fieldsets = UserAdmin.fieldsets + (
#         (None, {'fields': ('user_type', 'gender', 'birth_date', 'has_car')}),
#     )
#     add_fieldsets = UserAdmin.add_fieldsets + (
#         (None, {'fields': ('user_type', 'gender', 'birth_date', 'has_car')}),
#     )
#     list_filter = []

# admin.site.register(CustomUser, CustomUserAdmin)