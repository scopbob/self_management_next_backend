from django.db import models

# Create your models here.
from django.db import models
from accounts.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Category(models.Model):
    def __str__(self):
      return self.name

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=32)


class Todo(models.Model):
  def __str__(self):
      return self.title


  def clean(self):
     if self.due < self.start:
        raise ValidationError("Due must be after Start")


  user = models.ForeignKey(User, on_delete=models.CASCADE)
  title = models.CharField(max_length=50)
  text = models.TextField(max_length=500, blank=True)
  due = models.DateTimeField()
  start = models.DateTimeField()
  progress = models.IntegerField(default=0, validators=[MaxValueValidator(100), MinValueValidator(0)])
  category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

  PRIORITY_CHOICES = {
    "Hi":"high",
    "Md":"middle",
    "Lo":"low"
  }
  priority = models.CharField(max_length=3, choices=PRIORITY_CHOICES, default="Md")


class Progress(models.Model):
   def __str__(self):
      return f"{self.user}'s Progress"

   user = models.OneToOneField(User, on_delete=models.CASCADE)
   within_due_lte20_num = models.IntegerField(default=0)
   within_due_lte40_num = models.IntegerField(default=0)
   within_due_lte60_num = models.IntegerField(default=0)
   within_due_lte80_num = models.IntegerField(default=0)
   within_due_lte100_num = models.IntegerField(default=0)
   out_due_num = models.IntegerField(default=0)
