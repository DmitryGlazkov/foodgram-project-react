![.github/workflows/main.yml](https://github.com/DmitryGlazkov/foodgram-project-react/actions/workflows/main.yml/badge.svg)

# **Foodgram**

**Ссылка на проект:** https://ypstudyhost.hopto.org/

**Вход в панель администатора:**
- **Логин: Admin**
- **Пароль: 1234**

Ресурс для публикации кулинарных рецептов. Позволяет публиковать, редактировать, удалять свои рецепты, просматривать чужие, подписываться на автора, добавлять рецепты в избранное, формировать список покупок из ингридиентов, входящих в рецепт, а также выгружать этот список в текстовом формате.

## Использованные технологии:
 - Python
 - Django
 - Django REST framework
 - Nginx
 - Gunicorn
 - Docker
 - PostgreSQL
 - React
 - Certbot

## Как развернуть проект на удалённом сервере:

* Клонируйте репозиторий:
```
    git clone git@github.com:DmitryGlazkov/foodgram-project-react.git
```

* Установите docker и docker-compose на удалённый сервер:
```
    sudo apt install docker.io
    sudo apt install docker-compose
```

* В файле docker-compose.production.yml редуктируйте имя пользователя DockerHub, копируйте на удаленный сервер:
```
    scp docker-compose.production.yml <username>@<host>:/home/<username>/
```
* На удалённом сервере создайте файл .env и впишите:
```
    POSTGRES_USER=<user>
    POSTGRES_PASSWORD=<password>
    POSTGRES_DB=<db name>
    DB_HOST=db
    DB_PORT=5432
    SECRET_KEY=<your secret key>
    DEBUG=True/False
    ALLOWED_HOSTS=<your ip / host>
```
* Для работы с Workflow добавьте в Secrets GitHub переменные окружения:
```
    DOCKER_PASSWORD=<DockerHub password>
    DOCKER_USERNAME=<DockerHub username>
    HOST=<ip>
    USER=<host username>
    PASSPHRASE=<host passphrase>
    SSH_KEY=<host SSH-key>
    TELEGRAM_TO=<chat id>
    TELEGRAM_TOKEN=<telegram token>
```
* Выполните ```git push``` на DockerHub.
* После деплоя проекта на удалённый сервер, создайте суперпользователя:
```
   sudo docker-compose.production.yml exec backend python manage.py createsuperuser
```

## Автор

[Дмитрий Глазков](https://github.com/DmitryGlazkov)