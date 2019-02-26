from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def home_view(request, *args, **kwargs):
    return HttpResponse("<h1>Home</h1>")

def login_view(request, *args, **kwargs):
    return render(request, "login/login.html", {})


def signup_view(request, *args, **kwargs):
    return render(request, "signup/signup.html", {})


def search_view(request, *args, **kwargs):
    return render(request, "search/search.html", {})
