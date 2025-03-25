from ninja import Router
from ninja_jwt.authentication import JWTAuth
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.middleware.csrf import get_token

from ninja_jwt.routers.blacklist import blacklist_router
from ninja_jwt.routers.obtain import obtain_pair_router, sliding_router
from ninja_jwt.routers.verify import verify_router

from .schemas import UserSchemaIn, UserSchemaOut, PasswordSchema
from .models import User

router = Router()

auth_router = Router()
auth_router.add_router("token", tags=["Auth"], router=obtain_pair_router)  # トークン取得 & リフレッシュ
auth_router.add_router("", tags=["Auth"], router=sliding_router)  # Sliding Token 用
auth_router.add_router("", tags=["Auth"], router=verify_router)  # トークンの検証
auth_router.add_router("", tags=["Auth"], router=blacklist_router)  # ブラックリスト登録
router.add_router("/auth", tags=["Auth"], router=auth_router)

@router.post("", tags=["Account"], response=UserSchemaOut)
def create_user(request, data: UserSchemaIn):
  user = User(email=data.email)
  password = data.password
  user.validate_and_set_password(password)
  user.full_clean()  # ValidationErrorの場合apiproject/api.py/django_validation_errorが呼び出される
  user.save()
  return user

@router.put("/update_password", tags=["Account"], response=UserSchemaOut, auth=JWTAuth())
def update_password(request, data: PasswordSchema):
  user = request.auth
  password = data.password
  user.validate_and_set_password(password)
  user.save()
  return user

@router.delete("", tags=["Account"], auth=JWTAuth())
def delete_user(request):
  user=request.auth
  user.delete()
  return {"success": True}
