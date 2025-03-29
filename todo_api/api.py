from ninja import Router
from django.shortcuts import get_object_or_404
from typing import List
from ninja_jwt.authentication import JWTAuth
from .models import Todo, Category
from .schemas import TodoSchemaIn, TodoSchemaOut, CategorySchema

router = Router(auth=JWTAuth())

todo_router = Router(tags=["Todo"])

@todo_router.post("/create_todo")
def create_todo(request, payload: TodoSchemaIn):
  payload_dict = payload.dict()

  user = request.auth
  if payload_dict["category"] and payload_dict["category"]!=0:
    payload_dict["category"] = get_object_or_404(Category, user=user, id=payload_dict["category"])
  elif payload_dict["category"]==0:
    payload_dict.pop("category")
  todo = Todo(user=user, **payload_dict)
  todo.full_clean()
  todo.save()
  return {"id": todo.id}

@todo_router.get("/{todo_id}", response=TodoSchemaOut)
def get_todo(request, todo_id: int):
  user=request.auth
  todo = get_object_or_404(Todo, user=user, id=todo_id)

  return todo

@todo_router.get("", response=List[TodoSchemaOut])
def list_todos(request):
  user = request.auth
  todos = Todo.objects.filter(user=user)
  return todos

@todo_router.put("/{todo_id}")
def update_todo(request, todo_id: int, payload: TodoSchemaIn):
  payload_dict = payload.dict()
  user=request.auth
  todo = get_object_or_404(Todo, user=user, id=todo_id)
  if payload_dict["category"] and payload_dict["category"]!=0:
    payload_dict["category"] = get_object_or_404(Category, user=user, id=payload_dict["category"])
  elif payload_dict["category"]==0:
    payload_dict.pop("category")

  for attr, value in payload_dict.items():
    setattr(todo, attr, value)
  todo.full_clean()
  todo.save()
  return {"success": True}

@todo_router.delete("/{todo_id}")
def delete_todo(request, todo_id: int):
  user=request.auth
  todo = get_object_or_404(Todo, user=user, id=todo_id)
  todo.delete()
  return {"success": True}

router.add_router("", router=todo_router)


category_router = Router(tags=["Category"])

@category_router.post("/create_category")
def create_category(request, payload: CategorySchema):
  payload_dict = payload.dict()
  user = request.auth
  category = Category(user=user, **payload_dict)
  category.full_clean()
  category.save()
  return {"id": category.id}

@category_router.get("/{category_id}", response=CategorySchema)
def get_category(request, category_id: int):
  user=request.auth
  category = get_object_or_404(Category, user=user, id=category_id)
  return category

@category_router.get("", response=List[CategorySchema])
def list_categories(request):
  user = request.auth
  categorys = Category.objects.filter(user=user)
  return categorys

@category_router.put("/{category_id}")
def update_category(request, category_id: int, payload: CategorySchema):
  user=request.auth
  category = get_object_or_404(Category, user=user, id=category_id)
  for attr, value in payload.dict().items():
    setattr(category, attr, value)
  category.save()
  return {"success": True}

@category_router.delete("/{category_id}")
def delete_category(request, category_id: int):
  user=request.auth
  category = get_object_or_404(Category, user=user, id=category_id)
  category.delete()
  return {"success": True}

router.add_router("category", router=category_router)
