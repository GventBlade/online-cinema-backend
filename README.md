# Online Cinema API

A professional backend service for an online cinema platform. This project showcases modern Python development practices, asynchronous API design, and automated infrastructure.

## Implemented Features (Project Scope)
1. **Authorization & Authentication:** Secure registration, JWT-based login (access/refresh tokens), and Role-Based Access Control (User, Moderator, Admin).
2. **Movie Catalog:** Full-featured catalog with searching, filtering (by genre, year, rating), and sorting capabilities.
3. **Shopping Cart:** Ability for users to manage their movie selections before purchasing.
4. **Order Management:** Transformation of cart items into orders with status tracking.
5. **Dependency Management:** Built with **Poetry** for reliable environment reproducibility.
6. **Containerization:** Fully dockerized environment using **Docker Compose** (API, PostgreSQL, Redis).
7. **API Documentation:** Interactive **Swagger/OpenAPI** documentation for all endpoints.
8. **Automated Testing:** High code coverage using **Pytest** for business logic and API endpoints.

## Tech Stack
- **Python 3.13**
- **FastAPI** (Web framework)
- **Poetry** (Dependency management)
- **PostgreSQL** (Database)
- **SQLAlchemy** (ORM)
- **Alembic** (Database migrations)
- **Docker & Docker Compose** (Containerization)

## Getting Started

### Prerequisites
- Python 3.13+
- Poetry installed

### Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/GventBlade/online-cinema-backend.git](https://github.com/GventBlade/online-cinema-backend.git)
   cd online-cinema-backend
   
2. Install dependencies:

Bash
poetry install
Running the Application
To start the development server:

Bash
poetry run fastapi dev app/main.py
The API will be available at http://127.0.0.1:8000.

Interactive documentation (Swagger UI) can be found at http://127.0.0.1:8000/docs.
# Cinema Deployment Checked
