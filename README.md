# Blog API

[![python](https://img.shields.io/badge/Python-3.10-3776AB.svg?style=flat\&logo=python\&logoColor=white)](https://www.python.org)
[![Django](https://img.shields.io/badge/Django-3.2-092E20.svg?style=flat\&logo=django\&logoColor=white)](https://www.djangoproject.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-4169E1.svg?style=flat\&logo=postgresql\&logoColor=white)](https://www.postgresql.org)
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

## **Infrastructure & Deployment**

1. **Load Balancer**: Distribute traffic (e.g., AWS ALB).
2. **App Layer**: Django served by **Gunicorn**, optionally behind Nginx.
3. **Database**: Managed PostgreSQL instance (Multi-AZ) for high availability.
4. **Cache**: Redis for caching post lists or heavy queries.
5. **Observability**: Prometheus + Grafana for metrics; ELK or Datadog for logging.

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

## **Docker**

* `docker-compose.dev.yml` for development.
* `Dockerfile` for production.

```bash
# Build images
docker compose -f docker-compose.dev.yml build

# Start services
docker compose -f docker-compose.dev.yml up
```

---

## **Testing & TDD**

We use **pytest** alongside Django's test framework:

```bash
poetry run pytest --cov=.
```

Tests reside in `tests/` covering models and API endpoints.

