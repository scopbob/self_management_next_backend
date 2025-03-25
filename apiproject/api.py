from ninja import NinjaAPI
from todo_api.api import router as todo_router
from accounts.api import router as accounts_router

api = NinjaAPI()

api.add_router("/todo", router=todo_router)
api.add_router("/account/",tags=["Account"], router=accounts_router)

#エラー処理
from django.core.exceptions import ValidationError
def get_validation_errors(e: ValidationError) -> dict:
    if hasattr(e, "message_dict"):
        return e.message_dict
    return {"non_field_errors": e.messages}


@api.exception_handler(ValidationError)
def django_validation_error(request, exc: ValidationError):
    error_dict = get_validation_errors(exc)
    return api.create_response(
        request,
        {
            "detail": [
                {
                    "type": "unknown_type",
                    "loc": ["body", "payload", key],
                    "msg": error_dict[key],
                }
                for key in error_dict
            ]
        },
        status=400,
    )
