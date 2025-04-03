from django.urls import path
from .views import (TaskListView,
                    toggle_task_status,
                    TaskCreateView,
                    TaskUpdateView,
                    TaskDeleteView,
                    RegisterView,
                    tag_list,
                    tag_create,
                    tag_edit,
                    tag_confirm_delete)

urlpatterns = [
    path("", TaskListView.as_view(), name="home"),
    path("register/", RegisterView.as_view(), name="register"),
    path("tags/", tag_list, name="tag-list"),
    path("tags/create/", tag_create, name="tag-create"),
    path("tags/<int:pk>/edit/", tag_edit, name="tag-edit"),
    path("tags/<int:pk>/confirm_delete/", tag_confirm_delete, name="tag-delete"),
    path("toggle/<int:pk>/", toggle_task_status, name="toggle-task"),
    path("task/new/", TaskCreateView.as_view(), name="task-create"),
    path("tasks/<int:pk>/edit/", TaskUpdateView.as_view(), name="task-edit"),
    path("tasks/<int:pk>/delete/", TaskDeleteView.as_view(), name="task-delete"),
]

app_name = "todolist"
