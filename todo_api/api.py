from ninja import Router
from django.shortcuts import get_object_or_404
from django.db.models import Q
from typing import List
from ninja_jwt.authentication import JWTAuth
from .models import Todo, Category
from .schemas import TodoSchemaIn, TodoSchemaOut, CategorySchemaIn, CategorySchemaOut

router = Router(auth=JWTAuth())

todo_router = Router(tags=["Todo"])

@todo_router.post("/create")
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


@todo_router.get("", response=List[TodoSchemaOut])
def list_todos(request, limit: int=None, offset: int=None, search: str=None, category: int=None, order: str=None, reverse: bool=False):
  user = request.auth
  todos = Todo.objects.filter(user=user)

  # Filter
  if search is not None:
    todos = todos.filter(Q(title__contains=search)|Q(text__contains=search)|Q(category__name__contains=search))
  if category is not None:
    todos = todos.filter(category__id=category)

  # Order
  if order is not None:
    todos = todos.order_by(order)
  if reverse:
    todos = todos.reverse()

  # Slice
  if (limit is not None) and (offset is not None):
    todos = todos[offset:offset+limit]
  return todos

@todo_router.get("/count")
def count_todos(request, search: str=None):
  user = request.auth
  todos = Todo.objects.filter(user=user)
  if search != None:
    todos = todos.filter(Q(title__contains=search)|Q(text__contains=search)|Q(category__name__contains=search))
  return todos.count()

@todo_router.get("/{todo_id}", response=TodoSchemaOut)
def get_todo(request, todo_id: int):
  user=request.auth
  todo = get_object_or_404(Todo, user=user, id=todo_id)
  return todo

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

@category_router.post("/create")
def create_category(request, payload: CategorySchemaIn):
  payload_dict = payload.dict()
  user = request.auth
  category = Category(user=user, **payload_dict)
  category.full_clean()
  category.save()
  return {"id": category.id}

@category_router.get("", response=List[CategorySchemaOut])
def list_categories(request, limit: int=None, offset: int=None, search: str=None, ids:List[int]=None):
  user = request.auth
  categories = Category.objects.filter(user=user)
  if search is not None:
    categories = categories.filter(Q(name__contains=search)|Q(color__contains=search))
  if ids is not None:
    categories = categories.filter(id__in=ids)
  if (limit is not None) and (offset is not None):
    categories = categories[offset:offset+limit]
  return categories


@category_router.get("/count")
def count_categories(request, search: str=None):
  user = request.auth
  categories = Category.objects.filter(user=user)
  if search != None:
    categories = categories.filter(Q(name__contains=search)|Q(color__contains=search))
  return categories.count()


@category_router.get("/{category_id}", response=CategorySchemaOut)
def get_category(request, category_id: int):
  user=request.auth
  category = get_object_or_404(Category, user=user, id=category_id)
  return category

@category_router.put("/{category_id}")
def update_category(request, category_id: int, payload: CategorySchemaIn):
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

router.add_router("category/", router=category_router)
