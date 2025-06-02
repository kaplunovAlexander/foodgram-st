
---

# Приложение для публикации рецептов

Веб-приложение, позволяющее пользователям публиковать рецепты, добавлять их в избранное и формировать список покупок. Предусмотрены регистрация, авторизация и подписки на других пользователей.
Фронтенд и бэкенд приложения запускаются в Docker-контейнерах.

## Автор

**Каплунов Александр Александрович**
[GitHub](https://github.com/username)
[Email](mailto:your.email@example.com)

## Технологии

* Python 3.10
* Django 4.x
* Django REST Framework
* Postgres
* Nginx
* Gunicorn
* Docker / Docker Compose
* React (фронтенд)

## Как запустить проект локально

### 1. Клонировать репозиторий

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo/infra
```

### 2. Создать `.env` файл

Создайте `.env` файл в папке `infra/` (если ещё нет):

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Запустить контейнеры

```bash
docker-compose up
```

Контейнер `frontend` соберёт статику и завершит работу. Остальные контейнеры (`backend`, `db`, `nginx`) останутся активными.

### 4. Применить миграции и создать суперпользователя

```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

### 5. Проверка

* Фронтенд доступен по адресу: [http://localhost](http://localhost)
* Спецификация API (Swagger): [http://localhost/api/docs/](http://localhost/api/docs/)

---

> Полезно почитать:
> [Markdown на GitHub](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
> [Markdown в Azure DevOps](https://docs.microsoft.com/ru-ru/azure/devops/project/wiki/markdown-guidance?view=azure-devops)

---

