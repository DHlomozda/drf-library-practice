# 📚 Library Service API

A comprehensive library management system built with Django REST Framework that allows users to manage books, borrowings, and payments.

## 🚀 Features

### Books Management 📖
- CRUD operations for books
- Inventory tracking
- Daily fee calculation
- Book availability status

### Borrowing System 🔄
- Create and manage book borrowings
- Track borrowing history
- Automatic inventory updates
- Expected return date management
- Overdue book tracking

### Payment Integration 💳
- Stripe payment processing
- Support for regular payments and fines
- Payment session management
- Success and cancel payment flows
- Fine calculation for overdue books

### User Management 👥
- JWT authentication
- User roles (admin/regular user)
- Access control for different operations
- User-specific borrowing history

### Notifications 📢
- Telegram bot integration
- Automatic notifications for:
  - New borrowings
  - Overdue books
  - Daily overdue checks

### Security 🛡️
- JWT token authentication
- Role-based access control
- Secure payment processing
- Environment variable management

________________

## 🛠️ Tech Stack

<div align="center">

| Technology          | Description                   |
|---------------------|------------------------------|
| 🐍 Python 3.11+     | Backend language             |
| 🌐 Django 5.2       | Web framework                |
| 🧱 Django REST      | API creation                 |
| 🐘 PostgreSQL       | Database                     |
| 🎯 Celery & Redis   | Background tasks & scheduling|
| 💳 Stripe API       | Payment processing           |
| 🤖 Telegram Bot API | Notification system          |
| 🔑 JWT Auth         | Authentication method        |

</div>

##  📊 Model diagram

![Untitled](https://github.com/user-attachments/assets/cdc6d0b1-0f4c-4642-93e1-135e41f1eae1)
__________________
## ⚙️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/library-service.git
cd library-service
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create .env file based on .env.sample:
```bash
cp .env.sample .env
```

5. Fill in the environment variables in .env file:
```
SECRET_KEY=your_secret_key
DEBUG=True
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

6. Run migrations:
```bash
python manage.py migrate
```

7. Create superuser:
```bash
python manage.py createsuperuser
```

8. Run the development server:
```bash
python manage.py runserver
```
______________________
## 📘 API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/api/schema/swagger/

______________________
## ⏱ Running with Celery

1. Start Redis server
2. Start Celery worker:
```bash
celery -A library_service worker -l info
```
3. Start Celery beat:
```bash
celery -A library_service beat -l info
```
_____________________
## 🐳 Docker Setup

### Prerequisites
- Docker
- Docker Compose

### Running with Docker

1. Build and start the containers:
```bash
docker-compose up --build
```

2. Run migrations:
```bash
docker-compose exec web python manage.py migrate
```

3. Create superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

### Docker Services

The application consists of the following services:
- `web`: Django application
- `db`: PostgreSQL database
- `redis`: Redis server for Celery
- `celery_worker`: Celery worker for background tasks
- `celery_beat`: Celery beat for scheduled tasks

### Environment Variables

Create a `.env` file in the project root with the following variables:
```
SECRET_KEY=your_secret_key
DEBUG=True
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
POSTGRES_DB=library_db
POSTGRES_USER=library_user
POSTGRES_PASSWORD=library_password
```

### Useful Docker Commands

- View logs:
```bash
docker-compose logs -f
```

- Stop all containers:
```bash
docker-compose down
```
