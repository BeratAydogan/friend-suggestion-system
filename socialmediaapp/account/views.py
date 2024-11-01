from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

# Create your views here.
def login_request(request):
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect("index")
            else:
                return render(request, "account/login.html", {"error": "Hesabınız aktif değil! Hesabınızı doğrulayınız."})
        else:
            return render(request, "account/login.html", {
                "error": "Giriş başarısız! Kullanıcı adı ve şifrenizi kontrol ediniz. "})
    return render(request, "account/login.html")


def register_request(request):
    if request.user.is_authenticated:
        return redirect("anasayfa")
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        name = request.POST["name"]
        surname = request.POST["surname"]
        password = request.POST["password"]
        repassword = request.POST["repassword"]

        if password == repassword:
            if not User.objects.filter(username=username).exists():
                if username is "":
                    return render(request, "account/register.html",
                                  {"error": "Kullanıcı adı boş olmamalı.", "name": name, })
                else:
                    if User.objects.filter(email=email).exists():
                        return render(request, "account/register.html",
                                      {"error": "Bu email başkası tarafından kullanılmakta.", "name": name, })
                    else:
                        user = User.objects.create_user(username=username, email=email, first_name=name, last_name=surname,
                                                        password=password)
                      
                     
                        user.is_active = True
                        user.save()


                        return redirect("login")
            else:
                return render(request, "account/register.html",
                              {"error": "Bu kullanıcı adı başkası tarafından kullanılmakta.",
                               "name": name,

                               })
        else:
            return render(request, "account/register.html",
                          {"error": "Parola eşleşmiyor tekrar deneyiniz.", "name": name, })

    return render(request, "account/register.html", )




def logout_request(request):
    logout(request)
    return redirect("index")

def get_users(request):
    users = User.objects.all()

    return render(request, "index.html",{"users":users})