from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponse

# Authenticatiom
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate

# Forms and models
from app_login.models import Profile
from app_login.forms import ProfileForm, SignUpForm

# Messages
from django.contrib import messages

# Create your views here.
def sign_up(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully!")
            return HttpResponseRedirect(reverse("app_login:login"))
    return render(request, "app_login/sign_up.html", context={"form": form})


def login_user(request):
    form = AuthenticationForm()
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("app_shop:home"))
    return render(request, "app_login/login.html", context={"form": form})


@login_required
def logout_user(request):
    logout(request)
    messages.warning(request, "You are logged out")
    return HttpResponseRedirect(reverse("app_shop:home"))


@login_required
def user_profile(request):
    profile = Profile.objects.get(user=request.user)
    form = ProfileForm(instance=profile)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Changes saved")
            form = ProfileForm(instance=profile)
    return render(request, "app_login/change_profile.html", context={"form": form})
