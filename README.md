# Blog API

[![python](https://img.shields.io/badge/Python-3.10-3776AB.svg?style=flat\&logo=python\&logoColor=white)](https://www.python.org)
[![Django](https://img.shields.io/badge/Django-4.2-092E20.svg?style=flat\&logo=django\&logoColor=white)](https://www.djangoproject.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1.svg?style=flat\&logo=postgresql\&logoColor=white)](https://www.postgresql.org)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge\&logo=docker\&logoColor=white)](https://www.docker.com)

# **Simple Blogging Platform API**

## **Introduction**

This challenge involves building a RESTful API using Django and PostgreSQL for a simple blogging platform. The core features include:

* Managing **BlogPost** entities with title and content.
* Managing **Comment** entities associated with each BlogPost.

## **Acceptance Criteria**

### **Methodology**

We will adopt **Behavior-Driven Development (BDD)** to ensure clear requirements and traceability of scenarios.

### **User Stories**

1. **As** a content creator,
   **I want** to create new posts,
   **So that** I can share articles.

2. **As** a content creator,
   **I want** to list all posts with comment counts,
   **So that** I can view engagement.

3. **As** a reader,
   **I want** to view a specific post with its comments,
   **So that** I can read feedback.

4. **As** a reader,
   **I want** to add comments to a post,
   **So that** I can participate in the discussion.

### **BDD Scenarios**

#### **Feature: List Posts**

```gherkin
Scenario: List all posts with comment counts
  Given multiple posts exist in the system
  When I send a GET request to /api/posts
  Then I should receive a JSON array of posts
  And each post should include title and comment_count
```

#### **Feature: Create Post**

```gherkin
Scenario: Create a new post
  Given I am authenticated as a content creator
  When I send a POST request to /api/posts with title and content
  Then a new BlogPost is created
  And the response returns id, title, and content
```

#### **Feature: Retrieve Post**

```gherkin
Scenario: Retrieve a specific post
  Given a post with ID 42 exists
  When I send a GET request to /api/posts/42
  Then the response should include title, content, and comments[]
```

#### **Feature: Add Comment**

```gherkin
Scenario: Add a comment to a post
  Given a post with ID 42 exists
  When I send a POST request to /api/posts/42/comments with author_name and content
  Then a new Comment is associated with post 42
  And the response returns id, author_name, content, and created_at
```

---

## **Domain Models**

| **BlogPost**                                |   |
| ------------------------------------------- | - |
| id: UUID                                    |   |
| title: str                                  |   |
| content: Text                               |   |
| created\_at: DateTime                       |   |
| updated\_at: DateTime                       |   |
| comments: List\[Comment] (reverse relation) |   |

| **Comment**                 |   |
| --------------------------- | - |
| id: UUID                    |   |
| post: ForeignKey → BlogPost |   |
| author\_name: str           |   |
| content: Text               |   |
| created\_at: DateTime       |   |

---

## **API Routes**

| Endpoint                   | Method | Action                                                 |
| -------------------------- | ------ | ------------------------------------------------------ |
| `/api/posts`               | GET    | List all posts with title and comment\_count           |
| `/api/posts`               | POST   | Create a new BlogPost                                  |
| `/api/posts/{id}`          | GET    | Retrieve a specific BlogPost with details and comments |
| `/api/posts/{id}/comments` | POST   | Add a new Comment to the specified BlogPost            |

---

## **Code Quality & Pre-commit Hooks**

The project uses pre-commit hooks to ensure code quality and security.

### **Install Pre-commit Hooks**

```bash
# Install pre-commit hooks
uv run pre-commit install

# Install all hooks (including pip-audit)
uv run pre-commit install --all-files
```

### **Available Hooks**

- **Black**: Code formatting (88 chars line length)
- **Isort**: Import sorting (Black-compatible)
- **Flake8**: Linting and style checking
- **MyPy**: Static type checking
- **Bandit**: Security vulnerability scanning
- **Vulture**: Dead code detection
- **Pip-Audit**: Dependency vulnerability scanning

### **Run Hooks Manually**

```bash
# Run all hooks on all files
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run black --all-files

# Run hooks on staged files only
uv run pre-commit run
```

### **Skip Hooks (Emergency Only)**

```bash
# Skip hooks for a commit (not recommended)
git commit -m "message" --no-verify
```

---

## **Infrastructure & Deployment**

1. **Load Balancer**: Distribute traffic (e.g., AWS ALB).
2. **App Layer**: Django served by **Gunicorn**, optionally behind Nginx.
3. **Database**: Managed PostgreSQL instance (Multi-AZ) for high availability.
4. **Cache**: Redis for caching post lists or heavy queries.
5. **Observability**: Prometheus + Grafana for metrics; ELK or Datadog for logging.

---

## **Docker Development**

The project includes Docker configuration for easy development setup.

### **Prerequisites**

- Docker
- Docker Compose

### **Quick Start with Docker**

```bash
# Copy environment file
cp env.example .env

# Start all services (Django, PostgreSQL, Redis)
docker compose -f docker-compose.dev.yml up

# Access the application
# Web: http://localhost:8000
# Database: localhost:5432
# Redis: localhost:6379
```

### **Docker Services**

- **Web**: Django application with hot reload
- **DB**: PostgreSQL 15-alpine
- **Redis**: Redis 7-alpine

### **Useful Docker Commands**

```bash
# Start in background
docker compose -f docker-compose.dev.yml up -d

# View logs
docker compose -f docker-compose.dev.yml logs -f web

# Stop all services
docker compose -f docker-compose.dev.yml down

# Rebuild and start
docker compose -f docker-compose.dev.yml up --build

# Access web container
docker compose -f docker-compose.dev.yml exec web bash

# Run Django commands
docker compose -f docker-compose.dev.yml exec web python manage.py shell
```

---

## **Production Deployment**

The Docker setup is for development only. For production deployment, consider these options:

### **Cloud Platforms**

#### **Google Cloud Platform (GCP)**
- **Cloud Run**: Auto-scaling, serverless
- **GKE**: Kubernetes for complex applications
- **Cloud SQL**: Managed PostgreSQL
- **Memorystore**: Managed Redis

#### **AWS**
- **ECS/Fargate**: Container orchestration
- **RDS**: Managed PostgreSQL
- **ElastiCache**: Managed Redis

---

### **Redis Caching**

The API implements Redis caching for improved performance:

- **GET /api/posts**: Cached for 5 minutes
- **GET /api/posts/{id}**: Cached for 5 minutes
- **Cache Invalidation**: Automatically invalidated on new posts/comments

Cache keys:
- `posts_list`: List of all posts with comment count
- `post_detail_{id}`: Individual post details with comments
- `post_comments_{id}`: Comments for specific post

---

## **Database**

We chose **PostgreSQL** because:

* ACID compliance and referential integrity.
* Advanced indexing and full-text search capabilities.
* Mature ecosystem and community support.

---

## **Dependency Management**

This project uses [Uv](https://github.com/astral-sh/uv) as the dependency manager for Python, which is a fast, modern alternative to pip. All dependencies are specified in `pyproject.toml`.

### Install Uv

```bash
pip install uv
```

### Create and activate the virtual environment

```bash
uv venv
uv venv exec python -m pip install --upgrade pip
```

### Install dependencies

```bash
uv sync
```

### Run Django commands

```bash
uv run python manage.py migrate
uv run python manage.py runserver
```

### Add new dependencies

```bash
uv pip install <pacote>
uv pip freeze > requirements.txt
```

---

## **Testing**

The project includes comprehensive tests with pytest, achieving over 90% code coverage.

### **Run Tests**

```bash
# Run all tests
uv run python -m pytest

# Run with coverage report
uv run python -m pytest --cov=blog --cov-report=html

# Run specific test file
uv run python -m pytest blog/tests/test_posts_endpoints.py

# Run tests with verbose output
uv run python -m pytest -v
```

### **Test Structure**

- **`blog/tests/test_models.py`**: Model tests (creation, relationships, timestamps)
- **`blog/tests/test_serializers.py`**: Serializer validation tests
- **`blog/tests/test_posts_endpoints.py`**: Post API endpoint tests
- **`blog/tests/test_comments_endpoints.py`**: Comment API endpoint tests
- **`blog/tests/conftest.py`**: Shared fixtures and test data

---

## Environment Configuration

The project uses separate settings for development and production:

- **Development**: `settings.dev` (default)
- **Production**: `settings.prod`

To specify which settings to use:

```bash
# Development (default)
DJANGO_SETTINGS_MODULE=settings.dev uv run python manage.py runserver

# Production
DJANGO_SETTINGS_MODULE=settings.prod uv run python manage.py runserver
```

### Environment Variables

Copy `env.example` to `.env` and configure your environment variables:

```bash
cp env.example .env
```

