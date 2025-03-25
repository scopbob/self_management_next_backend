from django.apps import AppConfig


class TodoApiConfig(AppConfig):
  default_auto_field = 'django.db.models.BigAutoField'
  name = 'todo_api'
  def ready(self):
      import todo_api.signals  # ここでシグナルをインポート
