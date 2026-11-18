from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .forms import ProfileForm
from .models import User
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import RegisterForm
from .models import ConsentRecord


def home(request):
    return render(request, 'home.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        ip = request.META.get('REMOTE_ADDR')
        for consent in (ConsentRecord.TERMS, ConsentRecord.PERSONAL):
            ConsentRecord.objects.create(user=user, consent_type=consent, ip_address=ip)
        login(request, user)
        messages.success(request, 'Добро пожаловать! Аккаунт создан.')
        return redirect('profile_edit')

    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile_me(request):
    """Открывает мой собственный профиль."""
    return redirect('profile_detail', pk=request.user.pk)


def profile_detail(request, pk):
    """Страница профиля любого студента. Почта и телефон не передаются в шаблон."""
    owner = get_object_or_404(User, pk=pk, is_active=True)
    return render(request, 'accounts/profile.html', {
        'owner': owner,
        'profile': owner.profile,
        'is_me': request.user == owner,
    })


@login_required
def profile_edit(request):
    """Редактировать можно только свой профиль: берём его из request.user."""
    form = ProfileForm(request.POST or None, request.FILES or None,
                       instance=request.user.profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Профиль сохранён.')
        return redirect('profile_me')
    return render(request, 'accounts/profile_edit.html', {'form': form})