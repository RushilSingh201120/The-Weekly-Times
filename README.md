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
- MariaDB
- MySQL Client (`mysqlclient`)
- Django Token Authentication
- HTML
- CSS
- JavaScript
- Python Requests
- Python Dotenv

## 4. Project Structure

The project is organised into the following main components:

- `weekly_times_project/` – Main Django project configuration.
- `news/` – Main application containing models, views, serializers, permissions, signals, API endpoints and automated tests.
- `templates/` – HTML templates used by the application.
- `static/` – Static assets, including CSS.
- `manage.py` – Django management utility.
- `requirements.txt` – Python dependencies.
- `.env` – Environment-specific configuration and sensitive settings.

## 5. Installation and Setup

### Prerequisites

Ensure the following are installed:

- Python
- MariaDB
- Git
- A code editor such as Visual Studio Code

### Step 1: Clone the Repository


git clone <RushilSingh201120>
cd The_Weekly_Times


Replace the repository URL with the actual GitHub repository address.

### Step 2: Create a Virtual Environment


python -m venv venv


Activate it on Windows PowerShell:

powershell
.\venv\Scripts\Activate.ps1


### Step 3: Install Dependencies


pip install -r requirements.txt


### Step 4: Configure Environment Variables

Create a `.env` file in the project root directory (the same directory as `manage.py`).

Configure the following environment variables:


SECRET_KEY=your-django-secret-key
DB_NAME=your-database-name
DB_USER=your-database-username
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=3306

Gmail SMTP configuration

GMAIL_EMAIL=your-gmail-address
GMAIL_APP_PASSWORD=your-gmail-app-password

# Internal API configuration
INTERNAL_API_KEY=your-internal-api-key

The application loads database credentials from environment variables using `python-dotenv`.

**Important:** Never upload your `.env` file to GitHub or expose passwords, secret keys or API credentials in a public repository.

### Step 5: Configure the Database

Create the MariaDB database and database user using the credentials configured in your `.env` file.

Ensure the database settings in `settings.py` correctly load these environment variables.

### Step 6: Apply Database Migrations


python manage.py makemigrations
python manage.py migrate


### Step 7: Create a Superuser


python manage.py createsuperuser


### Step 8: Run the Development Server


python manage.py runserver


Open the following address in your browser:


http://127.0.0.1:8000/


## 6. REST API

The application provides REST API functionality through Django REST Framework.

| Endpoint | Method | Description |
|---|---|---|
| `/api/token/` | POST | Obtain an authentication token |
| `/api/articles/` | GET, POST | Retrieve articles or create an article as a Journalist |
| `/api/articles/subscribed/` | GET | Retrieve approved articles from subscribed journalists and publishers |
| `/api/articles/<id>/` | GET, PUT, PATCH, DELETE | Retrieve or manage an individual article |
| `/api/newsletters/` | GET, POST | Retrieve or create newsletters |
| `/api/newsletters/<id>/` | GET, PUT, PATCH, DELETE | Retrieve or manage an individual newsletter |
| `/api/publishers/` | GET, POST | Retrieve or create publishers |
| `/api/publishers/<id>/` | GET, PUT, PATCH, DELETE | Retrieve or manage an individual publisher |
| `/api/approved/` | POST | Internal endpoint for approved article submissions |

### API Authentication

The REST API uses Django REST Framework authentication, including Token Authentication and Session Authentication.

Users must authenticate before accessing protected endpoints. Access to operations is restricted according to the user's role and permissions.

The internal approved article endpoint uses an API key when configured.

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


python manage.py test news


## 8. Security and Access Control

The application uses Django authentication, custom user roles, groups and permissions to restrict access to protected functionality.

Sensitive configuration values are stored in environment variables rather than hardcoded into the application.

API operations are protected according to the user's role, and internal article submissions are protected using an API key when configured.

## 9. Database

The application uses MariaDB as its relational database.

Django models define the relationships between users, publishers, articles and newsletters. Database migrations are used to manage changes to the database schema.

