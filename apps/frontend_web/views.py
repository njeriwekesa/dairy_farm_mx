from django.shortcuts import render, redirect

def register_view(request):
    return render(request, "register.html")

def login_view(request):
    return render(request, "login.html")

def dashboard_view(request):
    return render(request, "dashboard.html")