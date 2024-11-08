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


# user data analyze

class UserLogins(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_logins")
    no_logins = models.PositiveIntegerField(default=0)
    failed_attempts = models.PositiveIntegerField(default=0)

    # no_devices = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.user.username + "_logins"

    class Meta:
        verbose_name = "User Login"
        verbose_name_plural = "User Logins"
        db_table = "UserLogins_TB"


class UserIP(models.Model):
    user_logins = models.ForeignKey(UserLogins, on_delete=models.CASCADE, related_name="ips")
    ip = models.CharField(max_length=20)
    date = models.DateTimeField(auto_now_add=True)
    failed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user_logins.user.username) + "_ip"

    class Meta:
        verbose_name = "User IPs"
        verbose_name_plural = "User IP"
        db_table = "UserIP_TB"


class UserDevice(models.Model):
    user_logins = models.ForeignKey(UserLogins, on_delete=models.CASCADE, related_name="devices")
    device_name = models.CharField(max_length=100)
    is_phone = models.BooleanField(default=False)
    browser = models.CharField(max_length=100)
    os = models.CharField(max_length=100)

    @classmethod
    def get_user_device(cls, user_agent, user_logins_id):
        return cls(device_name=user_agent["device_name"], is_phone=user_agent["is_phone"],
                   browser=user_agent["browser"], os=user_agent["os"], user_logins_id=user_logins_id)

    def __str__(self):
        return str(self.user_logins.user.username) + "_device"

    class Meta:
        verbose_name = "User Devices"
        verbose_name_plural = "User Device"
        db_table = "UserDevice_TB"
