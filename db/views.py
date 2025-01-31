from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView

from .forms import TaskForm, TagForm, RegisterForm
from .models import Task, Tag


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "db/home.html"
    context_object_name = "tasks"
    paginate_by = 3

    def get_queryset(self):
        queryset = Task.objects.all()

        tag_filter = self.request.GET.get("tag")
        if tag_filter:
            queryset = queryset.filter(tags__name=tag_filter)

        search_query = self.request.GET.get("search", "")
        if search_query:
            queryset = queryset.filter(content__icontains=search_query)

        return queryset.order_by("is_done", "-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["tags"] = Tag.objects.all()
        context["search_query"] = self.request.GET.get("search", "")

        if not context["tasks"]:
            context["no_tasks_message"] = "No tasks found"

        return context

@login_required
def toggle_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.is_done = not task.is_done
    task.save()
    return redirect("todolist:home")


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "db/task_form.html"
    success_url = reverse_lazy("todolist:home")

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "db/task_edit.html"
    context_object_name = "task"

    def get_success_url(self):
        return reverse_lazy("todolist:home")

class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "db/task_confirm_delete.html"
    context_object_name = "task"

    def get_success_url(self):
        return reverse_lazy("todolist:home")


@login_required
def tag_list(request):
    search_query = request.GET.get("search", "")

    if search_query:
        tags = Tag.objects.filter(name__icontains=search_query)
    else:
        tags = Tag.objects.all()

    paginator = Paginator(tags, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    no_tags_message = None
    if not tags:
        no_tags_message = "No Tags Found"

    return render(request, "db/tag_list.html", {
        "tags": page_obj,
        "search_query": search_query,
        "no_tags_message": no_tags_message,
    })

@login_required
def tag_create(request):
    if request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("todolist:tag-list")
    else:
        form = TagForm()
    return render(request, "db/tag_create.html", {"form": form})

@login_required
def tag_edit(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    if request.method == "POST":
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            return redirect("todolist:tag-list")
    else:
        form = TagForm(instance=tag)
    return render(request, "db/tag_update.html", {"form": form})

@login_required
def tag_delete(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    tag.delete()
    return redirect("todolist:tag-list")

@login_required
def tag_confirm_delete(request, pk):
    tag = get_object_or_404(Tag, pk=pk)

    if request.method == "POST":
        tag.delete()
        return redirect("todolist:tag-list")

    return render(request, "db/tag_confirm_delete.html", {"tag": tag})

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "db/register.html"
    success_url = reverse_lazy("todolist:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        return response