from django import forms
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from .models import User


class BootstrapMixin:
    """Добавляет Bootstrap-классы ко всем полям формы."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'


class RegisterForm(BootstrapMixin, forms.ModelForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)
    agree_terms = forms.BooleanField(label='Я принимаю пользовательское соглашение')
    agree_personal = forms.BooleanField(label='Я согласен на обработку персональных данных')

    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone']
        labels = {'full_name': 'ФИО', 'email': 'Электронная почта', 'phone': 'Номер телефона'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # По ТЗ эти поля обязательны
        self.fields['full_name'].required = True
        self.fields['phone'].required = True

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        domains = settings.COLLEGE_EMAIL_DOMAINS
        if domains and email.split('@')[-1] not in domains:
            raise forms.ValidationError('Нужна электронная почта колледжа.')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Эта почта уже зарегистрирована.')
        return email

    def clean_password1(self):
        password = self.cleaned_data['password1']
        validate_password(password)   # правила Django: длина, не слишком простой и т.д.
        return password

    def clean(self):
        data = super().clean()
        p1, p2 = data.get('password1'), data.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Пароли не совпадают.')
        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email                       # логин = почта
        user.set_password(self.cleaned_data['password1'])  # пароль хранится в зашифрованном виде
        if commit:
            user.save()
        return user

from django.contrib.auth.forms import AuthenticationForm


class LoginForm(BootstrapMixin, AuthenticationForm):
    username = forms.CharField(label='Электронная почта')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    def clean_username(self):
        return self.cleaned_data['username'].strip().lower()

from .models import UserProfile


class ProfileForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['display_name', 'avatar', 'bio', 'availability']
        widgets = {
            'avatar': forms.FileInput,
            'bio': forms.Textarea(attrs={'rows': 4}),
        }