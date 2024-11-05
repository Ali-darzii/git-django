from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    first_name = None
    last_name = None

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = "User_TB"


class GenderChoice(models.TextChoices):
    MALE = "M", "male"
    FEMALE = "F", "female"
    OTHER = "O", "other"


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_profile")
    avatar = models.ImageField(upload_to="images/users_avatar", blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    gender = models.CharField(max_length=1, choices=GenderChoice.choices, default=GenderChoice.OTHER)
    company = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "Users Profile"
        db_table = "UserProfile_TB"
