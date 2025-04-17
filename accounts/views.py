from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

User = get_user_model()


def user_login(request):
    next_url = request.GET.get("next", "my_app:home")

    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(
            request, email=email, password=password
        )  # Authenticate via email
        if user is not None:
            login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect(request.POST.get("next", next_url))
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "accounts/login.html", {"next": next_url})


def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


def user_register(request):
    next_url = request.GET.get("next", "my_app:home")
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)  # Hash the password
        user.save()
        login(request, user)
        return redirect(request.POST.get("next", next_url))

    return render(
        request,
        "accounts/register.html",
        {"next": next_url},
    )
