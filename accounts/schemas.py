from ninja import ModelSchema, Schema
from .models import User
from typing import Type, Dict
from ninja_jwt.schema import TokenObtainInputSchemaBase
from ninja_jwt.tokens import RefreshToken


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
    fields = ["email", "avatar"]

class PasswordSchema(ModelSchema):
  class Meta:
    model = User
    fields = ["password"]


class AvatarSchema(Schema):
  image: str


class MyTokenObtainPairOutSchema(Schema):
    refresh: str
    access: str
    email: str
    avatar: str


class MyTokenObtainPairInputSchema(TokenObtainInputSchemaBase):
    @classmethod
    def get_response_schema(cls) -> Type[Schema]:
        return MyTokenObtainPairOutSchema

    @classmethod
    def get_token(cls, user) -> Dict:
        values = {}
        refresh = RefreshToken.for_user(user)
        values["refresh"] = str(refresh)
        values["access"] = str(refresh.access_token)
        values["email"] = user.email
        values["avatar"] = user.avatar.url if user.avatar else ""
        print(values["avatar"])
        return values
