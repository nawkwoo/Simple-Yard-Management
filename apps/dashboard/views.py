import csv
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from .forms import CSVUploadForm
from io import TextIOWrapper
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'accounts/login.html')

@login_required
@login_required
def home(request):
    context = {
        'edit_url': reverse('edit:equipment-list'),
        'manage_url': reverse('view:view_page'),
        'order_url': reverse('dashboard:order'),
    }
    return render(request, 'dashboard/home.html', context)

@login_required
def order(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            csv_file_wrapper = TextIOWrapper(csv_file.file, encoding='utf-8')
            reader = csv.reader(csv_file_wrapper)
            
            for row in reader:
                print(row)  # 주문 처리해야함 (개발 전)
            
            messages.success(request, 'CSV 파일이 성공적으로 업로드되었습니다.')
            return redirect('dashboard:home')
    else:
        form = CSVUploadForm()
    
    return render(request, 'dashboard/order.html', {'form': form})