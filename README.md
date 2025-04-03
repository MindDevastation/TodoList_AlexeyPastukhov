# To-Do List

## Overview

This is a Django-based To-Do List application that allows users to manage their tasks efficiently. The project follows the MVC (Model-View-Controller) architecture and includes user authentication.

### Features

- User authentication (login/logout)

- Task creation, update, and deletion

- Task categorization and status management

- Pagination for better task organization

### Technologies Used

- Python

- Django

- SQLite3 (default database)

- HTML/CSS (templates)

### Project Structure

```
├── db
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│
├── templates
│   ├── db/
│   │   ├── home.html
│   │   ├── register.html
│   │   ├── tag_confirm_delete.html
│   │   ├── tag_create.html
│   │   ├── tag_list.html
│   │   ├── tag_update.html
│   │   ├── task_confirm_delete.html
│   │   ├── task_edit.html
│   │   ├── task_form.html
│   ├── includes/
│   │   ├── pagination.html
│   │   ├── sidebar.html
│   ├── registration/
│   │   ├── logged_out.html
│   │   ├── login.html
│   ├── base.html
│
├── todolist
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│
├── db.sqlite3
├── manage.py
├── README.md
├── requirements.txt
```
### Installation

**Prerequisites**

- Python 3.x

- pip (Python package manager)

**Steps**

1. Clone the repository:
```
git clone https://github.com/yourusername/todolist.git
cd todolist
```
2. Create and activate a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install dependencies:
```
pip install -r requirements.txt
```
4. Apply migrations:
```
python manage.py migrate
```
5. Create a superuser:
```
python manage.py createsuperuser
```
6. Run the development server:
```
python manage.py runserver
```
7. Open your browser and navigate to:
```
http://127.0.0.1:8000/
```
**Usage**

- Register/Login to manage your tasks

- Add, edit, and delete tasks from the dashboard

- Use the sidebar for navigation and task filtering
