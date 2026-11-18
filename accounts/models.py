from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    """Пользователь. Логин = электронная почта."""
    email = models.EmailField('Эл. почта', unique=True)
    full_name = models.CharField('ФИО', max_length=150, blank=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)

    def __str__(self):
        return self.email or self.username


class UserProfile(models.Model):
    """Публичная часть: то, что видят другие студенты."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField('Публичное имя', max_length=50, blank=True)
    avatar = models.ImageField('Фото', upload_to='avatars/', blank=True)
    bio = models.TextField('О себе', max_length=500, blank=True)
    availability = models.CharField('Когда доступен для встреч', max_length=200, blank=True)

    @property
    def public_name(self):
        # ФИО, почта и телефон публично НЕ показываются (требование ТЗ)
        if self.display_name:
            return self.display_name
        parts = self.user.full_name.split()
        return parts[0] if parts else 'Студент'

    def __str__(self):
        return self.public_name


class ConsentRecord(models.Model):
    """Запись о согласии пользователя (требование ТЗ, раздел 4.1)."""
    TERMS = 'terms'
    PERSONAL = 'personal_data'
    TYPES = [(TERMS, 'Пользовательское соглашение'),
             (PERSONAL, 'Обработка персональных данных')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consents')
    consent_type = models.CharField(max_length=20, choices=TYPES)
    document_version = models.CharField(max_length=20, default='1.0')
    accepted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f'{self.user} — {self.consent_type}'


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Как только создаётся пользователь, автоматически создаётся его профиль."""
    if created:
        UserProfile.objects.create(user=instance)