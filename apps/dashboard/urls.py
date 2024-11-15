from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),    # 초기 페이지 (로그인 전)
    path('home/', views.home, name='home'), # 로그인 후 첫 페이지
    path('order/', views.order, name='order'), # 주문 입력 페이지
]