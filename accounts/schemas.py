from ninja import ModelSchema
from .models import User

class UserSchemaIn(ModelSchema):
  class Meta:
    model = User
    fields = ["email", "password"]

class UserSchemaOut(ModelSchema):
  id: int
  class Meta:
    model = User
    fields = ["email"]

class PasswordSchema(ModelSchema):
  class Meta:
    model = User
    fields = ["password"]
