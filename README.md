# The Weekly Times – Django News Application

## 1. Project Overview

The Weekly Times is a Django-based news application that allows independent journalists and publishers to create and manage news articles and newsletters.

The application provides role-based access for Readers, Journalists and Editors. Journalists can publish independent or publisher-associated articles, Editors can review and approve articles, and Readers can view approved news content and subscribe to the journalists and publishers they follow.

When an article is approved, the application sends email notifications to relevant subscribers and submits the approved article to an internal REST API endpoint.

## 2. Main Features

### User Management and Authentication
- Custom user model with Reader, Journalist and Editor roles.
- Role-based access control using Django groups and permissions.
- User authentication and protected application functionality.

### Reader Functionality
- Browse approved news articles.
- View individual article details.
- Subscribe to and unsubscribe from journalists and publishers.
- View newsletters and their associated articles.
- Access articles from subscribed journalists and publishers through the REST API.

### Journalist Functionality
- Create, view, edit and delete their own articles.
- Submit articles for editorial approval.
- Create, view, edit and delete their own newsletters.
- Associate articles and newsletters with publishers where applicable.

### Editor Functionality
- Access the editorial review queue.
- Review and approve pending articles.
- Manage articles across journalists.
- Manage newsletters, including editing and deleting them.
- Manage publishers.

### Automated Notifications and Integration
- Email notifications are sent to relevant subscribers when an article is approved.
- Approved articles are submitted to the application's internal API endpoint.
- Approval and integration activity is recorded for tracking and error handling.

## 3. Technologies Used

- Python
- Django
- Django REST Framework
- MariaDB / MySQL
- MySQL Client (`mysqlclient`)
- Django Token Authentication
- HTML
- CSS
- JavaScript
- Python Requests
- Python Dotenv
- Sphinx
- Docker
- Docker Compose

## 4. Project Structure

The project is organised into the following main components:

- `weekly_times_project/` – Main Django project configuration.
- `news/` – Main application containing models, views, serializers, permissions, signals, API endpoints and automated tests.
- `templates/` – HTML templates used by the application.
- `static/` – Static assets, including CSS.
- `docs/` – Sphinx documentation source files and generated HTML documentation.
- `manage.py` – Django management utility.
- `requirements.txt` – Python dependencies.
- `Dockerfile` – Instructions for building the Django application image.
- `docker-compose.yml` – Configuration for running the Django application and MySQL database services.
- `.dockerignore` – Files excluded from the Docker build context.
- `.gitignore` – Files excluded from Git version control.

## 5. Installation and Setup

### Prerequisites

Ensure the following are installed:

- Python 3.14
- MariaDB or MySQL
- Git
- A code editor such as Visual Studio Code

### Step 1: Clone the Repository

Clone the GitHub repository:

```bash
git clone https://github.com/RushilSingh201120/The-Weekly-Times.git
```

Navigate into the project directory:

```bash
cd The-Weekly-Times
```

### Step 2: Create a Virtual Environment

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

Install the project dependencies:

```bash
python -m pip install -r requirements.txt
```

The requirements file includes the Django application dependencies and the Sphinx documentation packages.

### Step 4: Configure Environment Variables

Create a `.env` file in the project root directory, in the same directory as `manage.py`.

Add the following configuration, replacing the example values with your own credentials:

```env
# Django configuration
DJANGO_SECRET_KEY=your-django-secret-key
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database configuration
DB_NAME=weekly_times_db
DB_USER=weekly_times_user
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=3306

# Gmail SMTP configuration
GMAIL_EMAIL=your-gmail-address
GMAIL_APP_PASSWORD=your-gmail-app-password

# Internal API configuration
APPROVED_ARTICLE_API_URL=
INTERNAL_API_KEY=your-internal-api-key
```

The `APPROVED_ARTICLE_API_URL` setting can be left blank if an external approved-article destination is not being used.

The application uses `python-dotenv` to load environment variables from the `.env` file.

**Important:** Keep your `.env` file private. Do not commit it to GitHub or include real passwords, secret keys or API credentials in documentation.

### Step 5: Configure the Database

Start your MariaDB or MySQL service.

Open a terminal and log in to the database server:

```bash
mysql -u root -p
```

Enter your database administrator password when prompted.

Create the project database:

```sql
CREATE DATABASE weekly_times_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Create a database user:

```sql
CREATE USER 'weekly_times_user'@'localhost'
IDENTIFIED BY 'your-database-password';
```

Grant the user access to the project database:

```sql
GRANT ALL PRIVILEGES ON weekly_times_db.*
TO 'weekly_times_user'@'localhost';

FLUSH PRIVILEGES;
```

Exit the database console:

```sql
EXIT;
```

Ensure that the `DB_NAME`, `DB_USER` and `DB_PASSWORD` values in your `.env` file match the database and user you created.

### Step 6: Apply Database Migrations

Run Django's database migrations:

```bash
python manage.py migrate
```

### Step 7: Create a Superuser

Create an administrator account:

```bash
python manage.py createsuperuser
```

Follow the prompts to configure the account.

### Step 8: Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

Open the following address in your browser:

http://127.0.0.1:8000/

The Django administration interface is available at:

http://127.0.0.1:8000/admin/

## 6. REST API

The application provides REST API functionality through Django REST Framework.

### Available Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/token/` | POST | Obtain an authentication token |
| `/api/articles/` | GET, POST | Retrieve articles or create an article as an authorised Journalist |
| `/api/articles/subscribed/` | GET | Retrieve articles from subscribed journalists and publishers |
| `/api/articles/<id>/` | GET, PUT, PATCH, DELETE | Retrieve or manage an individual article |
| `/api/newsletters/` | GET, POST | Retrieve or create newsletters |
| `/api/newsletters/<id>/` | GET, PUT, PATCH, DELETE | Retrieve or manage an individual newsletter |
| `/api/publishers/` | GET, POST | Retrieve or create publishers |
| `/api/publishers/<id>/` | GET, PUT, PATCH, DELETE | Retrieve or manage an individual publisher |
| `/api/approved/` | POST | Internal endpoint for approved article submissions |

### API Authentication

The REST API uses Django REST Framework authentication, including Token Authentication and Session Authentication.

The token endpoint accepts a POST request containing the user's login credentials. The returned token can then be used to authenticate requests to protected API endpoints.

Access to API operations is restricted according to the user's role and permissions.

The internal approved-article endpoint accepts POST requests and uses an API key supplied through the `X-API-Key` request header. The submitted article must have an approved status and include the required article information.

## 7. Automated Testing

The project includes automated Django tests covering application functionality, API access and role-based permissions.

The test suite covers:

- Authentication and unauthenticated access.
- Reader, Journalist and Editor permissions.
- Article creation, editing and deletion.
- Article approval by Editors.
- Reader subscription filtering.
- Newsletter creation and management.
- Publisher management.
- Email notifications.
- Internal API submissions.
- Handling of notification and integration failures.

Run the automated tests using:

```bash
python manage.py test news
```

Run Django's system checks using:

```bash
python manage.py check
```

## 8. Security and Access Control

The application uses Django authentication, custom user roles, groups and permissions to restrict access to protected functionality.

Sensitive configuration values are stored in environment variables rather than hardcoded into the application.

API operations are protected according to the user's role, and internal article submissions are protected using an API key.

The supplied Django development server is intended for development and testing, not production deployment.

## 9. Database

The application uses MariaDB or MySQL as its relational database.

Django models define the relationships between users, publishers, articles and newsletters. Database migrations are used to manage changes to the database schema.

The Docker Compose configuration uses MySQL 8.4 as its database service.

## 10. Sphinx Documentation

The project uses Sphinx to generate technical documentation from Python docstrings.

The documentation source files are located in:

```text
docs/
└── source/
    ├── conf.py
    ├── index.rst
    ├── modules.rst
    └── news.rst
```

The Sphinx configuration uses the autodoc, napoleon and viewcode extensions to document the application's Python modules, classes and functions.

### Build the Documentation

Ensure that the project dependencies have been installed, then run:

```bash
sphinx-build -b html docs/source docs/build/html
```

After the build completes, open the generated documentation:

```text
docs/build/html/index.html
```

The generated HTML documentation includes the project overview and Python code reference.

## 11. Docker Containerisation

The project includes Docker support to run the Django application and its MySQL database in containers.

### Prerequisites

Ensure the following are installed and running:

- Docker Desktop
- Docker Engine
- Docker Compose

### Step 1: Configure Environment Variables

Ensure that the project root contains a `.env` file with the Django, database and email configuration described in Section 5.

Docker Compose also requires the following database administrator password:

```env
MYSQL_ROOT_PASSWORD=your-mysql-root-password
```

Use the same database name, application database username and application database password as the other database settings.

Do not commit the `.env` file to version control.

### Step 2: Build the Docker Image

From the project root directory, run:

```bash
docker compose build
```

This builds the Django application image using the project Dockerfile and installs the required dependencies.

### Step 3: Start the Containers

Run:

```bash
docker compose up
```

Docker Compose starts the MySQL database and Django web application.

The web container waits for the database health check and automatically applies Django database migrations before starting the development server.

### Step 4: Access the Application

Open the application in your browser:

http://localhost:8000/

The administration interface is available at:

http://localhost:8000/admin/

### Step 5: Stop the Containers

Press `Ctrl+C` in the terminal running Docker Compose, then execute:

```bash
docker compose down
```

The MySQL database uses a persistent Docker volume, so database records are retained when the containers are stopped and removed.

**Important:** Avoid using `docker compose down -v` unless you intentionally want to delete the persistent database volume and its stored data.

### Docker Hub Image

The Docker image is available from Docker Hub:

https://hub.docker.com/r/rushilsingh2011/the-weekly-times

## 12. Project Repository

The source code and project history are available on GitHub:

https://github.com/RushilSingh201120/The-Weekly-Times

The repository includes the Django application, Python dependencies, Sphinx documentation, Docker configuration and project README.
