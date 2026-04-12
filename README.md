## Ссылка на развернутый проект

https://foodgramir.duckdns.org/

---

## Описание проекта

Foodgram — это сервис для публикации рецептов. Пользователи могут создавать рецепты, добавлять их в избранное, формировать список покупок и скачивать его в виде файла формата txt.
Автор реализовывал backend-часть проекта.

---

## Стек технологий

- Python 3.12
- Django
- Django REST Framework
- PostgreSQL
- Docker
- Docker Compose
- Gunicorn
- Nginx

---

## Как развернуть проект на сервере

1. Клонировать репозиторий:

```bash
git clone git@github.com:IhuliR/foodgram.git
cd foodgram
```

2. Создать файл .env:

SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=your_domain

DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

3. Запустить контейнеры:

```bash
docker compose up -d
```

4. Выполнить миграции и собрать статику:

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic --noinput
```

5. Загрузить данные:

```bash
docker compose exec backend python manage.py load_data
```

---

## Как запустить проект локально (опционально)

1. Перейти в директорию backend:

```bash
cd backend
```

2. Создать и активировать виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
```

3. Установить зависимости:

```bash
pip install -r requirements.txt
```

4. Применить миграции:

```bash
python manage.py migrate
```

5. Запустить сервер:
```bash
python manage.py runserver
```