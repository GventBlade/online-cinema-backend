# Online Cinema API

A production-ready asynchronous backend service for an online cinema platform. This project demonstrates modern Python engineering standards, scalable infrastructure setup, asynchronous background tasks, and automated cloud deployment.

---

## 🌐 Live Demo on AWS
The application is fully deployed and accessible on AWS EC2 cloud infrastructure:
👉 **[Interactive Swagger API Documentation](http://16.171.160.208:8000/docs)**

---

## 🚀 Key Features & Project Scope

1. **Robust Authentication & Security:** Secure user registration and login utilizing JWT tokens (Asymmetric/Symmetric workflows with Access & Refresh tokens). Implements Role-Based Access Control (RBAC) across `User`, `Moderator`, and `Admin` tiers.
2. **Advanced Movie Catalog:** High-performance catalog browsing featuring multi-parameter search, complex filtering (by genres, release year, age ratings), and dynamic sorting.
3. **Shopping Cart System:** Persistent user carts allowing seamless management of movie licenses/tickets before checking out.
4. **Order & Payment Lifecycle:** Conversion of cart instances into formal orders integrated with mock payment flows and state management.
5. **Asynchronous Architecture:** Background processing for notifications and heavy operations handled via Celery worker pools.
6. **Isolated Environments:** 100% containerized environment leveraging multi-container Docker orchestration for predictable staging and production behavior.
7. **Automated CI/CD:** Complete integration with GitHub Actions that executes test suites and automatically deploys verified code directly to AWS EC2 via SSH pipelines.

---

## 🛠 Tech Stack & Ecosystem

* **Core Framework:** Python 10+ / FastAPI (Asynchronous Server Gateway Interface Framework)
* **Dependency Management:** Poetry (Strict lockfile environment reproducibility)
* **Data Storage:** PostgreSQL (Relational Database) & SQLAlchemy (Async ORM)
* **Migrations Management:** Alembic (Linear database schema version control)
* **Caching & Message Broker:** Redis (In-memory data structure store)
* **Task Queue:** Celery (Distributed background task execution)
* **Testing Engine:** Pytest (High-coverage suite for integration & unit testing)
* **Infrastructure:** Docker & Docker Compose / AWS EC2 / GitHub Actions

---

## 📦 Architecture & Infrastructure Layout

The system is decoupled into isolated services managed by Docker Compose:
* `cinema_api` — The main FastAPI web service handling incoming REST traffic.
* `cinema_db` — PostgreSQL database instance persisting structural application data.
* `cinema_redis` — In-memory caching and queuing broker layer.
* `cinema_worker` — Celery asynchronous worker process handling background tasks.

---

## 🏁 Getting Started

### Prerequisites
* Docker & Docker Compose installed on your local machine **OR** Python 3.12+ with Poetry.

### 1. Repository Setup & Environment Configuration
Clone the repository and enter the workspace directory:
```bash
git clone [https://github.com/GventBlade/online-cinema-backend.git](https://github.com/GventBlade/online-cinema-backend.git)
cd online-cinema-backend
Create your local environment file by replicating the provided sample template:

Bash
cp .env.sample .env
💡 Open the .env file and fill in your custom secret keys, Stripe tokens, and SMTP credentials as described in the configuration comments.

2. Multi-Container Orchestration (Recommended)
To automatically pull images, compile the application, and start all services in detached (background) mode:

Bash
docker compose up --build -d
3. Database Schema Provisioning
Apply linear database migrations via Alembic inside the running API container to build your schemas and tables:

Bash
docker compose exec api poetry run alembic upgrade head
The system will now boot and be reachable locally:

Local API Base: http://localhost:8000

Interactive API Documentation (Swagger UI): http://localhost:8000/docs

🧪 Running the Test Suite
To validate business logic, endpoints validation, and access controls, execute the automated testing pipeline inside the Docker runtime environment:

Bash
docker compose exec api poetry run pytest
