from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import TaskForm, TagForm
from .models import Tag, Task
from django.utils import timezone
from datetime import timedelta


# Models tests
class TagModelTest(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(name="Test Tag")

    def test_tag_unique(self):
        tag_2 = Tag(name="Test Tag")
        with self.assertRaises(Exception):
            tag_2.save()


class TaskModelTest(TestCase):
    def setUp(self):
        self.tag1 = Tag.objects.create(name="Work")
        self.tag2 = Tag.objects.create(name="Home")

        self.task = Task.objects.create(
            content="Finish the project",
            deadline=timezone.now() + timedelta(days=1),
            is_done=False
        )
        self.task.tags.add(self.tag1, self.tag2)

    def test_task_tags(self):
        task = self.task
        self.assertIn(self.tag1, task.tags.all())
        self.assertIn(self.tag2, task.tags.all())

    def test_task_is_done_toggle(self):
        task = self.task
        task.is_done = True
        task.save()
        self.assertTrue(task.is_done)

    def test_task_deadline(self):
        task = self.task
        self.assertEqual(task.deadline.date(), (timezone.now() + timedelta(days=1)).date())


# View tests
class TaskViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")
        self.tag = Tag.objects.create(name="Test Tag")
        self.task = Task.objects.create(
            content="Test task 1",
            created_at=timezone.now(),
            is_done=False
        )
        self.task.tags.add(self.tag)

    def test_task_list_view(self):
        response = self.client.get(reverse("todolist:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test task 1")
        self.assertContains(response, "Tags")

    def test_task_create_view(self):
        response = self.client.get(reverse("todolist:task-create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create a New Task")
        response = self.client.post(reverse("todolist:task-create"), {
            "content": "New Task",
            "tags": [self.tag.pk],
            "is_done": False
        })
        self.assertRedirects(response, reverse("todolist:home"))
        task = Task.objects.get(content="New Task")
        self.assertEqual(task.content, "New Task")

    def test_task_update_view(self):
        response = self.client.get(reverse("todolist:task-edit", args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Task")
        response = self.client.post(reverse("todolist:task-edit", args=[self.task.pk]), {
            "content": "Updated Task",
            "tags": [self.tag.pk],
            "is_done": True
        })
        self.assertRedirects(response, reverse("todolist:home"))
        self.task.refresh_from_db()
        self.assertEqual(self.task.content, "Updated Task")

    def test_task_delete_view(self):
        response = self.client.get(reverse("todolist:task-delete", args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Are you sure you want to delete")
        response = self.client.post(reverse("todolist:task-delete", args=[self.task.pk]))
        self.assertRedirects(response, reverse("todolist:home"))
        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(pk=self.task.pk)


class TaskStatusToggleViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")
        self.tag = Tag.objects.create(name="Test Tag")
        self.task = Task.objects.create(
            content="Test task 1",
            created_at=timezone.now(),
            is_done=False
        )
        self.task.tags.add(self.tag)

    def test_toggle_task_status_to_done(self):
        response = self.client.post(reverse("todolist:toggle-task", args=[self.task.pk]))
        self.assertRedirects(response, reverse("todolist:home"))
        self.task.refresh_from_db()
        self.assertTrue(self.task.is_done)

    def test_toggle_task_status_to_undone(self):
        self.task.is_done = True
        self.task.save()

        response = self.client.post(reverse("todolist:toggle-task", args=[self.task.pk]))
        self.assertRedirects(response, reverse("todolist:home"))
        self.task.refresh_from_db()
        self.assertFalse(self.task.is_done)


class TagViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")
        self.tag = Tag.objects.create(name="Test Tag")

    def test_tag_list_view(self):
        response = self.client.get(reverse("todolist:tag-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tags")
        self.assertContains(response, self.tag.name)

    def test_tag_create_view(self):
        response = self.client.get(reverse("todolist:tag-create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add New Tag")
        response = self.client.post(reverse("todolist:tag-create"), {
            "name": "New Tag"
        })
        self.assertRedirects(response, reverse("todolist:tag-list"))
        tag = Tag.objects.get(name="New Tag")
        self.assertEqual(tag.name, "New Tag")

    def test_tag_update_view(self):
        response = self.client.get(reverse("todolist:tag-edit", args=[self.tag.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Tag")
        response = self.client.post(reverse("todolist:tag-edit", args=[self.tag.pk]), {
            "name": "Updated Tag"
        })
        self.assertRedirects(response, reverse("todolist:tag-list"))
        self.tag.refresh_from_db()
        self.assertEqual(self.tag.name, "Updated Tag")

    def test_tag_delete_view(self):
        response = self.client.get(reverse("todolist:tag-delete", args=[self.tag.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Are you sure you want to delete")
        response = self.client.post(reverse("todolist:tag-delete", args=[self.tag.pk]))
        self.assertRedirects(response, reverse("todolist:tag-list"))
        with self.assertRaises(Tag.DoesNotExist):
            Tag.objects.get(pk=self.tag.pk)


class TaskFilterTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")
        self.tag1 = Tag.objects.create(name="Work")
        self.tag2 = Tag.objects.create(name="Personal")
        self.task1 = Task.objects.create(content="Task 1", is_done=False)
        self.task2 = Task.objects.create(content="Task 2", is_done=False)
        self.task1.tags.add(self.tag1)
        self.task2.tags.add(self.tag2)

    def test_filter_by_tag(self):
        response = self.client.get(reverse("todolist:home"), {"tag": "Work"})
        self.assertContains(response, "Task 1")
        self.assertNotContains(response, "Task 2")

    def test_filter_by_no_tag(self):
        response = self.client.get(reverse("todolist:home"), {"tag": ""})
        self.assertContains(response, "Task 1")
        self.assertContains(response, "Task 2")


class TaskSearchTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")
        self.task1 = Task.objects.create(content="Task 1", is_done=False)
        self.task2 = Task.objects.create(content="Task 2", is_done=True)
        self.task3 = Task.objects.create(content="Important Task 3", is_done=False)
        self.task4 = Task.objects.create(content="Task 4", is_done=True)

    def test_search_task_content(self):
        response = self.client.get(reverse("todolist:home"), {"search": "Task"})

        self.assertContains(response, "Task 1")
        self.assertContains(response, "Task 2")
        self.assertContains(response, "Important Task 3")

        self.assertNotContains(response, "Non-existing Task")

    def test_search_task_content_empty_result(self):
        response = self.client.get(reverse("todolist:home"), {"search": "Non-existing"})

        self.assertNotContains(response, "Task 1")
        self.assertNotContains(response, "Task 2")
        self.assertNotContains(response, "Important Task 3")

        self.assertContains(response, "No tasks found")

    def test_search_task_with_tag(self):
        tag = Tag.objects.create(name="Important")
        self.task1.tags.add(tag)
        self.task3.tags.add(tag)

        response = self.client.get(reverse("todolist:home"), {"search": "Task", "tag": "Important"})

        self.assertContains(response, "Task 1")
        self.assertContains(response, "Important Task 3")

        self.assertNotContains(response, "Task 2")
        self.assertNotContains(response, "Task 4")

    def test_search_task_empty_search(self):
        response = self.client.get(reverse("todolist:home"), {"search": ""})

        self.assertContains(response, "Task 1")
        self.assertContains(response, "Task 2")
        self.assertContains(response, "Important Task 3")


class TagSearchTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")
        Tag.objects.create(name="Work")
        Tag.objects.create(name="Personal")
        Tag.objects.create(name="Shopping")

    def test_search_tags(self):
        response = self.client.get(reverse("todolist:tag-list") + "?search=Work")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Work")
        self.assertNotContains(response, "Personal")
        self.assertNotContains(response, "Shopping")

        response = self.client.get(reverse("todolist:tag-list") + "?search=Personal")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Personal")
        self.assertNotContains(response, "Work")
        self.assertNotContains(response, "Shopping")

    def test_no_tags_found(self):
        response = self.client.get(reverse("todolist:tag-list") + "?search=NonExistentTag")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Tags Found")
        self.assertNotContains(response, "Work")
        self.assertNotContains(response, "Personal")
        self.assertNotContains(response, "Shopping")


# Form tests
class TaskFormTest(TestCase):

    def setUp(self):
        self.tag = Tag.objects.create(name="Test Tag")

    def test_valid_task_form(self):
        form_data = {
            "content": "Test Task",
            "tags": [self.tag.pk],
            "is_done": False
        }
        form = TaskForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_task_form(self):
        form_data = {
            "content": "",
            "tags": [self.tag.pk],
            "is_done": False
        }
        form = TaskForm(data=form_data)
        self.assertFalse(form.is_valid())


class TagFormTest(TestCase):

    def test_valid_tag_form(self):
        form_data = {"name": "New Tag"}
        form = TagForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_tag_form(self):
        form_data = {"name": ""}
        form = TagForm(data=form_data)
        self.assertFalse(form.is_valid())


# Auth tests
class AuthenticationTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")

    def test_login_view(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_login_user(self):
        response = self.client.post(reverse("login"), {
            "username": "testuser",
            "password": "password"
        })
        self.assertRedirects(response, reverse("todolist:home"))

    def test_logout_view(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("logout"))
        self.assertTemplateUsed(response, "registration/logged_out.html")


# Template tests
class TemplateTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

    def test_home_template(self):
        response = self.client.get(reverse("todolist:home"))
        self.assertTemplateUsed(response, "db/home.html")
        self.assertContains(response, "Todo List")

    def test_sidebar_template(self):
        response = self.client.get(reverse("todolist:home"))
        self.assertContains(response, "Navigation:")

    def test_tag_list_template(self):
        response = self.client.get(reverse("todolist:tag-list"))
        self.assertContains(response, "Tags")


# Other tests
class HomePagePaginationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

    def test_task_pagination(self):
        for i in range(15):
            Task.objects.create(content=f"Task {i}", is_done=False)

        response = self.client.get(reverse("todolist:home"))
        self.assertContains(response, "Next")
        self.assertNotContains(response, "Previous")

        response = self.client.get(reverse("todolist:home") + "?page=5")
        self.assertNotContains(response, "Next")
        self.assertContains(response, "Previous")

        response = self.client.get(reverse("todolist:home") + "?page=2")
        self.assertContains(response, "Next")
        self.assertContains(response, "Previous")


class TagPaginationTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")
        for i in range(15):
            Tag.objects.create(name=f"Tag {i + 1}")

    def test_pagination_on_tag_list_page(self):
        response = self.client.get(reverse("todolist:tag-list"))

        self.assertEqual(len(response.context["tags"]), 10)
        self.assertTemplateUsed(response, "db/tag_list.html")

    def test_pagination_second_page(self):
        response = self.client.get(reverse("todolist:tag-list") + "?page=2")

        self.assertEqual(len(response.context["tags"]), 5)
        self.assertTemplateUsed(response, "db/tag_list.html")

    def test_search_with_pagination(self):
        response = self.client.get(reverse("todolist:tag-list") + "?search=Tag 1")

        self.assertContains(response, "Tag 1")
        self.assertTemplateUsed(response, "db/tag_list.html")

        self.assertEqual(len(response.context["tags"]), 7)

    def test_pagination_with_search(self):
        response = self.client.get(reverse("todolist:tag-list") + "?search=Tag&page=2")

        self.assertTemplateUsed(response, "db/tag_list.html")
        self.assertContains(response, "Tag 1")
        self.assertEqual(len(response.context["tags"]), 5)
