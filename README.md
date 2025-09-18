# 🎭 Theatre API

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.6-green?logo=django)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16-red?logo=django)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)](https://www.docker.com/)

API service for theatre management written with Django REST Framework.

---

## 🚀 Features
- 🔑 JWT authentication  
- ⚙️ Admin panel: `/admin/`  
- 📖 API documentation (Swagger): `/api/docs/swagger/`
- 🎟 Manage reservations and tickets  
- 🎭 Create plays with genres and actors  
- 🏛 Create theatre halls  
- 🎫 Add performances
- 📅 Filtering for plays and performances
- 📄 Pagination for all pages

---

## 🛠 Installation

### 1. Local installation (via GitHub)

1. Install **PostgreSQL** and create a database.  
2. Clone the repository:
   ```bash
   git clone https://github.com/Kostenikov/drf-theatre-api.git
   cd drf-theatre-api
   ```
3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux / Mac
   venv\Scripts\activate    # Windows
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Create your own `.env` file based on **.env.sample**.  
6. Run migrations:
   ```bash
   python manage.py migrate
   ```
7. Start the development server:
   ```bash
   python manage.py runserver
   ```

---

### 2. Run with Docker

1. Make sure **Docker** is installed.  
2. Build and run containers:
   ```bash
   docker-compose up --build
   ```
3. (Optional) Import data from fixture:
   ```bash
   docker ps  # check running container ID
   docker exec -it <container_id> sh
   python manage.py loaddata import.json
   ```

---

## 🔐 Getting Access

1. Register a new user:  
   ```
   POST /api/accounts/register/
   ```
2. Get access token:  
   ```
   POST /api/accounts/token/
   ```
   
3. You can also use credentials from the fixture for quick login:

- **Admin**  
   Username: `admin`  
   Password: `Zaq12wsxcde3`
    
    
- **User**  
    Username: `user`  
    Password: `Zaq12wsxcde3`


---