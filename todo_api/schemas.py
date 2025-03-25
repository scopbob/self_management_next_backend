from ninja import ModelSchema
from .models import Todo, Category, Progress

class TodoSchemaIn(ModelSchema):
  class Meta:
    model = Todo
    exclude = ["id", "user"]

class TodoSchemaOut(ModelSchema):
  class Meta:
    model = Todo
    exclude = ["user"]

class CategorySchema(ModelSchema):
  class Meta:
    model = Category
    exclude = ["id", "user"]
