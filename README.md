# API для Yatube

REST API социальной сети Yatube: публикации с изображениями и сообществами,
комментарии и подписки на авторов. API позволяет читать публикации без
регистрации, а после аутентификации — создавать контент и подписываться
на пользователей. Изменять и удалять публикации и комментарии может только
их автор. Сообщества создаются администратором через админку Django.

Стек: Python, Django 5.1, Django REST Framework 3.15, Djoser, Simple JWT,
SQLite. Для зависимостей из `requirements.txt` используйте Python 3.10–3.13.

## Установка и запуск

Клонируйте репозиторий и перейдите в его каталог:

```bash
git clone https://github.com/KirillFPV/api-final-yatube.git
cd api-final-yatube
```

Создайте и активируйте виртуальное окружение (пример для Python 3.13):

```bash
python3.13 -m venv venv
source venv/bin/activate
```

В Windows окружение активируется командой `venv\Scripts\activate`.

Установите зависимости, выполните миграции и создайте администратора:

```bash
python -m pip install -r requirements.txt
python yatube_api/manage.py migrate
python yatube_api/manage.py createsuperuser
python yatube_api/manage.py runserver
```

Сервер доступен по адресу <http://127.0.0.1:8000/>.
Документация с форматами запросов и ответов: <http://127.0.0.1:8000/redoc/>.
Админка: <http://127.0.0.1:8000/admin/>. Пользователей и сообщества можно
создать в админке; регистрация через API не предусмотрена.
Изображения сохраняются в `yatube_api/media/`.

## Эндпоинты

Все адреса начинаются с `/api/v1/`.

| Адрес | Методы | Назначение |
| --- | --- | --- |
| `posts/` | GET, POST | Список и создание публикаций |
| `posts/{id}/` | GET, PUT, PATCH, DELETE | Работа с публикацией |
| `posts/{post_id}/comments/` | GET, POST | Список и создание комментариев |
| `posts/{post_id}/comments/{id}/` | GET, PUT, PATCH, DELETE | Работа с комментарием |
| `groups/` | GET | Список сообществ |
| `groups/{id}/` | GET | Информация о сообществе |
| `follow/` | GET, POST | Собственные подписки и подписка на автора |
| `jwt/create/` | POST | Получение access- и refresh-токенов |
| `jwt/refresh/` | POST | Обновление access-токена |
| `jwt/verify/` | POST | Проверка токена |

Чтение публикаций, комментариев и сообществ доступно всем. Запись требует
JWT-токен. Эндпоинт `follow/` доступен только аутентифицированным пользователям.
При попытке изменить чужой контент API возвращает `403`, при запросе,
требующем аутентификации, без токена — `401`.

## Примеры запросов

Получите JWT-токены, указав данные существующего пользователя:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/jwt/create/ \
  -H 'Content-Type: application/json' \
  -d '{"username": "alice", "password": "your-password"}'
```

Ответ содержит `access` и `refresh`. Подставьте значение `access` вместо
`ACCESS_TOKEN` в заголовок `Authorization: Bearer ACCESS_TOKEN`.
По умолчанию access-токен действует 5 минут, refresh-токен — 1 день.

Создайте публикацию:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/posts/ \
  -H 'Authorization: Bearer ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"text": "Моя первая публикация", "group": null}'
```

Поля `group` и `image` необязательны. Для загрузки изображения используйте
`multipart/form-data`, например `-F 'text=Фото' -F 'image=@photo.jpg'`.

Получите публикации с пагинацией:

```bash
curl 'http://127.0.0.1:8000/api/v1/posts/?limit=10&offset=0'
```

С параметром `limit` ответ содержит `count`, `next`, `previous`, `results`.
Без `limit` возвращается список всех публикаций. Публикации отсортированы
по дате публикации: сначала новые.

Добавьте комментарий к публикации с идентификатором `1`:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/posts/1/comments/ \
  -H 'Authorization: Bearer ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"text": "Спасибо за публикацию!"}'
```

Автор определяется по токену, публикация для комментария — по адресу запроса.

Подпишитесь на существующего пользователя `bob`:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/follow/ \
  -H 'Authorization: Bearer ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"following": "bob"}'
```

Ответ: `{"user": "alice", "following": "bob"}`.
Повторная подписка и подписка на себя возвращают `400` с описанием ошибки.

Найдите автора среди своих подписок:

```bash
curl 'http://127.0.0.1:8000/api/v1/follow/?search=bob' \
  -H 'Authorization: Bearer ACCESS_TOKEN'
```

Обновите access-токен:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/jwt/refresh/ \
  -H 'Content-Type: application/json' \
  -d '{"refresh": "REFRESH_TOKEN"}'
```

## Проверка проекта

Выполните из корня репозитория с активированным окружением:

```bash
pytest
flake8
python yatube_api/manage.py check
python yatube_api/manage.py makemigrations --check --dry-run
```

Коллекция запросов для Postman и инструкция находятся в
каталоге [postman_collection](postman_collection/README.md).
