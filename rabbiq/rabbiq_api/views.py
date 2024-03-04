from django.shortcuts import render,redirect
from django.contrib import messages

def lockout(request, credentials, *args, **kwargs):
    messages.error(request,'Account locked. Too many login attempts. Please contact the administrator.')
    return redirect('admin:index')
