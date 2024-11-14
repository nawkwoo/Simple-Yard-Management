from django.shortcuts import render
from django.http import HttpResponse

def view_page(request):
    return HttpResponse("This is the YMS View page.")