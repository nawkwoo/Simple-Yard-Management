from django.shortcuts import render
from django.http import HttpResponse

def edit_view(request):
    return HttpResponse("This is the YMS Edit page.")