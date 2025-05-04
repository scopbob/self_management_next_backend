from ninja import Router, Form
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.tokens import RefreshToken
from django.core.exceptions import ValidationError
import os
import requests
import base64
import uuid
from dotenv import load_dotenv
from django.conf import settings

from ninja_jwt.routers.blacklist import blacklist_router
from ninja_jwt.routers.obtain import obtain_pair_router, sliding_router
from ninja_jwt.routers.verify import verify_router

from .schemas import GithubSchema, TokenSchema, UserSchemaIn, UserSchemaOut, PasswordSchema, AvatarSchema
from .models import User

load_dotenv()
AUTH_GITHUB_ID = os.getenv("AUTH_GITHUB_ID")
AUTH_GITHUB_SECRET = os.getenv("AUTH_GITHUB_SECRET")

router = Router()

auth_router = Router()
auth_router.add_router("token", tags=["Auth"], router=obtain_pair_router)  # トークン取得 & リフレッシュ
auth_router.add_router("", tags=["Auth"], router=sliding_router)  # Sliding Token 用
auth_router.add_router("", tags=["Auth"], router=verify_router)  # トークンの検証
auth_router.add_router("", tags=["Auth"], router=blacklist_router)  # ブラックリスト登録


@auth_router.post("/github/token", response=TokenSchema)
def github_login(request, code: Form[str]):
    # GitHubからアクセストークンを取得
    token_res = requests.post(
        'https://github.com/login/oauth/access_token',
        headers={'Accept': 'application/json'},
        data={
            'client_id': AUTH_GITHUB_ID,
            'client_secret': AUTH_GITHUB_SECRET,
            'code': code,
        }
    )
    access_token = token_res.json().get('access_token')
    if not access_token:
        return {"detail": "GitHub token fetch failed"}

    # GitHub APIからユーザー情報を取得
    user_res = requests.get(
        'https://api.github.com/user',
        headers={'Authorization': f'Bearer {access_token}'}
    ).json()

    email_res = requests.get(
        'https://api.github.com/user/emails',
        headers={'Authorization': f'Bearer {access_token}'}
    ).json()

    # primary email を取得
    primary_email = next((e['email'] for e in email_res if e.get('primary')), None)
    if not primary_email:
        return {"detail": "Email not found"}

    # Djangoユーザーと紐付け（存在しなければ作成）
    user, created = User.objects.get_or_create(email=primary_email)
    if created:
        user.set_unusable_password()
        user.full_clean()
        user.save()
    # JWTを発行
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token


    return {"access_token": str(access), "refresh_token": str(refresh), "token_type": 'bearer'}

router.add_router("/auth", tags=["Auth"], router=auth_router)

@router.get("me", tags=["Account"], response=UserSchemaOut, auth=JWTAuth())
def get_my_user(request):
  user = request.auth
  return user

@router.post("avatar", tags=["Account"], auth=JWTAuth())
def set_avatar(request, data: AvatarSchema):
  user = request.auth

  if not data.image.startswith("data:image"):
        return {"error": "Invalid image format"}

  format, imgstr = data.image.split(";base64,")
  ext = format.split("/")[-1]
  file_name = f"{uuid.uuid4()}.{ext}"

  # 保存先パス
  file_path = os.path.join(settings.MEDIA_ROOT, "avatars", file_name)

  # 保存先フォルダ作成
  os.makedirs(os.path.dirname(file_path), exist_ok=True)

  # 古いアバターを削除（ファイルが存在すれば）
  if user.avatar:
      old_avatar_path = os.path.join(settings.MEDIA_ROOT, str(user.avatar))
      if os.path.exists(old_avatar_path):
          try:
              os.remove(old_avatar_path)
          except Exception as e:
              print(f"Failed to delete old avatar: {e}")

  # 画像保存
  with open(file_path, "wb") as f:
      f.write(base64.b64decode(imgstr))

  # 画像のURLをDBに保存
  user.avatar = f"avatars/{file_name}"
  user.save()

  return {
      "message": "Image saved",
      "url": f"{settings.MEDIA_URL}avatars/{file_name}",
  }

@router.post("", tags=["Account"], response=UserSchemaOut)
def create_user(request, data: UserSchemaIn):
    user = User.objects.filter(email=data.email).first()

    if user:
        # すでにユーザーが存在していて、パスワードが未設定の場合
        if not user.has_usable_password():
            user.set_password(data.password)
            user.full_clean()
            user.save()
            return user
        else:
            # パスワードが設定済みの場合 → 登録済みとしてバリデーションエラーを投げる
            raise ValidationError({"email": "この Eメールアドレス を持った User が既に存在します。"})
    else:
        # 新規作成
        user = User(email=data.email)
        user.validate_and_set_password(data.password)
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
