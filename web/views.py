from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from datetime import timedelta, date


#@login_required
def index(request):
    context = {
    }
    return render(request, 'index.html', context)
