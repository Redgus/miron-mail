from django.http import HttpResponse
from django.shortcuts import render, redirect
from main.models import *

def index(request):
    return render(request, 'index.html')
