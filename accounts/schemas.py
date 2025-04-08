from ninja import ModelSchema, Schema
from .models import User

class GithubSchema(Schema):
  redirect_uri: str
  code: str
  code_verifier: str
  grant_type: str = None

class TokenSchema(Schema):
  access_token: str
  refresh_token: str
  token_type: str = "bearer"

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
