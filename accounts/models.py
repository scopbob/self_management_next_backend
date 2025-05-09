from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
  email = models.EmailField(
    verbose_name = "Eメールアドレス",
    max_length = 255,
    unique = True,
  )
  avatar = models.ImageField(
    verbose_name = "アバター画像",
    upload_to = "avatars/",
    blank = True,
    null = True,
  )
  active = models.BooleanField(default=True)
  staff = models.BooleanField(default=False)
  admin = models.BooleanField(default=False)
  USERNAME_FIELD = 'email'
  objects = UserManager()

  def __str__(self):
      return self.email

  def has_perm(self, perm, obj=None):
      return self.admin

  def has_module_perms(self, app_label):
      return self.admin

  def validate_and_set_password(self, password):
    try:
      validate_password(password)
    except ValidationError as e:
      error_dict = {"password": e.messages}
      raise ValidationError(error_dict)
    self.set_password(password)

  @property
  def is_staff(self):
      return self.staff

  @property
  def is_admin(self):
      return self.admin

  @property
  def is_active(self):
      return self.active
