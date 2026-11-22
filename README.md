# TaskFlow API

Учебный backend-проект: REST API для управления задачами на **Python + FastAPI + SQLAlchemy**.
Подходит для демонстрации навыков backend-разработки в портфолио стажёра Python-разработчика.

## Возможности

- Создание, просмотр, редактирование и удаление задач (CRUD)
- Статусы: `todo`, `in_progress`, `done`
- Приоритеты: `low`, `medium`, `high` и необязательный срок выполнения
- Фильтрация по статусу и приоритету, поиск по названию, пагинация
- Статистика по статусам (`/api/v1/stats`)
- Валидация входных данных Pydantic и автоматическая документация Swagger
- Изолированные API-тесты (pytest), автоматическая проверка GitHub Actions
- SQLite для быстрого локального запуска или PostgreSQL + Docker Compose

## Технологии

Python 3.11+, FastAPI, Pydantic, SQLAlchemy 2, SQLite, PostgreSQL, pytest, Docker.

## Быстрый старт без Docker

1. Создать окружение из корня репозитория:

   **Windows PowerShell**

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements-dev.txt
   ```

   **Linux / macOS**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements-dev.txt
   ```

2. Запустить сервер:

   ```bash
   uvicorn app.main:app --reload
   ```

3. Открыть в браузере:

   - Swagger UI: http://127.0.0.1:8000/docs
   - Проверка здоровья: http://127.0.0.1:8000/health

По умолчанию используется SQLite (`taskflow.db` создаётся автоматически). Файл базы и `.env` исключены из Git.

## Запуск с PostgreSQL через Docker

При установленном Docker Desktop / Docker Engine:

```bash
docker compose up --build
```

API: http://127.0.0.1:8000/docs. PostgreSQL доступен с компьютера через порт `5433` (внутри Docker — `5432`). Данные хранятся в Docker volume.

```bash
docker compose down
```

> Учётные данные в `compose.yaml` предназначены **только для локальной разработки**. Не используйте их при публичном развёртывании.

Для использования **локально установленного PostgreSQL** без контейнера API скопируйте `.env.example` в `.env`, укажите `DATABASE_URL` и создайте базу данных вручную. Пример: `postgresql+psycopg://USER:PASSWORD@localhost:5432/DBNAME`.

## Пример запроса

Создать задачу (можно также через Swagger UI):

```bash
curl -X POST http://127.0.0.1:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn FastAPI","priority":"high","status":"todo"}'
```

Пример ответа, идентификатор и даты будут отличаться:

```json
{
  "id": 1,
  "title": "Learn FastAPI",
  "description": null,
  "status": "todo",
  "priority": "high",
  "due_date": null,
  "created_at": "2026-11-02T10:00:00",
  "updated_at": "2026-11-02T10:00:00"
}
```

Дополнительные примеры запросов: `examples/requests.http`.

## API

| Метод | Путь | Назначение |
| --- | --- | --- |
| `GET` | `/health` | Проверка работы приложения |
| `POST` | `/api/v1/tasks` | Создать задачу |
| `GET` | `/api/v1/tasks` | Список задач с фильтрами и пагинацией |
| `GET` | `/api/v1/tasks/{id}` | Получить задачу |
| `PATCH` | `/api/v1/tasks/{id}` | Изменить поля задачи |
| `DELETE` | `/api/v1/tasks/{id}` | Удалить задачу |
| `GET` | `/api/v1/stats` | Статистика задач |

Для `GET /api/v1/tasks` доступны параметры `status`, `priority`, `search`, `offset`, `limit` (1–100).

## Тесты и проверка стиля

```bash
pytest -q
ruff check .
```

Тесты используют отдельную SQLite в памяти, не затрагивая базу разработчика. GitHub Actions запускает тесты при каждом push / pull request.

## Структура проекта

```text
app/
  main.py            # Настройка приложения и жизненного цикла
  db.py              # Подключение к БД и сессии
  models.py          # SQLAlchemy-модели
  schemas.py         # Pydantic-схемы
  routers/tasks.py   # HTTP-эндпоинты и работа с запросами
tests/                # API-тесты
examples/requests.http
.github/workflows/    # CI: линтер и тесты
Dockerfile
compose.yaml
```

## Что стоит изучить перед собеседованием

1. Чем отличаются методы `GET`, `POST`, `PATCH`, `DELETE` и коды HTTP 200/201/204/404/422.
2. Что делают `Session`, `commit`, `refresh`, `select` в SQLAlchemy.
3. Зачем Pydantic-схемы отделены от ORM-моделей.
4. Как работают Dependency Injection (`Depends`) и тестовые переопределения зависимостей.
5. Почему для изменения структуры БД в продакшене нужны миграции (например, Alembic), а не `create_all`.

## Дальнейшее развитие

- Авторизация пользователей (JWT) и задачи, принадлежащие конкретному пользователю
- Миграции с Alembic
- Сортировка и фильтр просроченных задач
- Деплой и публичная демонстрация API

## Как опубликовать на GitHub

1. Создайте пустой репозиторий `taskflow-api` в https://github.com/new (не выбирайте авто-создание README).
2. Откройте терминал в папке проекта, выполните:

   ```bash
   git init
   git add .
   git commit -m "Initial TaskFlow API"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/taskflow-api.git
   git push -u origin main
   ```

   Замените `YOUR_USERNAME` на ваш GitHub username. Для HTTPS-пуша нужен способ входа, поддерживаемый GitHub (например, Git Credential Manager / токен), не пароль аккаунта.

3. Добавьте ссылку на репозиторий в резюме **после того, как запустите и разберёте код**.

## Описание для резюме

> **TaskFlow API — pet-project (Python, FastAPI, SQLAlchemy, PostgreSQL, Docker, pytest)**. Разработал REST API для управления задачами: CRUD, фильтрация, поиск и пагинация. Настроил взаимодействие с PostgreSQL через SQLAlchemy, контейнеризацию Docker Compose, API-тестирование с pytest и CI в GitHub Actions.

Указывайте только технологии, которые вы действительно запускали и можете объяснить.

## Примечание

Это учебный сервис без аутентификации, разграничения прав и миграций БД. Не предназначен для хранения личных данных и публичного продакшен-развёртывания в текущем виде.
