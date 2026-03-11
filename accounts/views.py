from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileUpdateForm, RegisterForm, UserUpdateForm
from .models import Profile


def register(request):
    if request.user.is_authenticated:
        return redirect("store:product_list")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect("store:product_list")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    # Создать профиль если не существует
    profile_obj, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile_obj)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Профиль успешно обновлён!")
            return redirect("accounts:profile")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile_obj)

    from orders.models import Order

    orders = Order.objects.filter(user=request.user)[:5]

    return render(
        request,
        "accounts/profile.html",
        {
            "u_form": u_form,
            "p_form": p_form,
            "orders": orders,
        },
    )
