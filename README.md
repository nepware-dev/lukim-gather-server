# Lukim Gather Server

Repository for Lukim Gather Server

## Table of Contents
- [Requirement](#requirement)
- [Install](#install)
- [Datasets](#datasets)
- [Translation](#translation)
- [License](#license)


## Requirement
  - Git
  - [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
  - Python 3.9+
  - Django 3.2+
  - Django 3.2+
  - PostGIS 3.1+
  - PostgreSQL 13+

## Install
### Clone the repositary
```bash
git clone --branch develop https://github.com/undp-png/lukim-gather-server.git && cd lukim-gather-server
```
### Setup using docker-compose 

1. Create external-service docker network `docker network create external-services`
2. If server is setup for local environment than soft link `docker/docker-compose.dev.yml` else link `docker/docker-compose.prod.yml` for production
    - For development/testing `ln -s docker/docker-compose.dev.yml docker-compose.yml`
    - For staging/production `ln -s docker/docker-compose.prod.yml docker-compose.yml`
3. Create `.env` file from `.env.example` and set appropriate and required environmental variable as explained in `.env.example`
4. If either postgres or redis is required than run command `ln -s docker/external_services.yml external-services.yml` and  `docker-compose -f external-services.yml up -d` (Note:- Only postgres or redis can be run by using command `docker-compose -f external-services.yml up -d <NAME>` where `<NAME>` is replaced by either `db` or `redis` respectively.)
    - If you have setup any other database instead of sqlite3 then server needs database to be created before starting server
    - To create database run command `docker exec db psql -U postgres -c 'create database DATABASE_NAME;'.`. Replace DATABASE_NAME with actual database
5. Run `docker-compose up -d` to start both server and celery worker or `docker-compose up -d server` to start server only. To do task in background celery should be running.
6. Execute `docker-compose exec server sh` and run command `./manage.py createsuperuser` if super user is not created
7. Access server using url http://localhost:8000 and access admin using http://localhost:8000/admin

### Post-installation
1. Apply the [Django fixtures](https://docs.djangoproject.com/en/dev/howto/initial-data/#providing-data-with-fixtures) defined in the `fixtures` folder:

```bash
docker-compose exec container_name poetry run ./manage.py loaddata survey/fixtures/category.json  # Add protected area categories
```

## Datasets

### Region

| Attribute name | Label | Type   | Description |
| -------------- | ----- | ------ | ----------- |
| name          | Name | string   | Region name |
| code          | Code | string   | Region code |
| boundary    | Boundary | string   | Region boundary |

### Protectd Area Category

| Attribute name | Label | Type   | Description |
| -------------- | ----- | ------ | ----------- |
| title          | Title | string   | Category title |
| description    | Description | string   | Category description |

### Happening Survey

| Attribute name | Label | Type   | Description |
| -------------- | ----- | ------ | ----------- |
| title          | Title | string   | Survey title |
| description    | Description | string   | Survey description |
| sentiment      | Sentiments | string   | sentiments |
| attachment     | Attachments | file   | attachments |
| location       | Location | string   | Survey co-ordinates |
| boundary       | Boundary | string   | Survey boundary area |
| status         | Status | string   | Survey answer status |
| improvement    | Improvement | string   | Survey improvement status. |
| is_public      | Is Public? | boolean   | Flat to determine wheter submitted survey is public or not. |
| is_test        | Is Test? | boolean   | Flag to determine whether submitted survey is test or not. |

## Translation

To translate Lukim Gather visit [Hosted Weblate](https://hosted.weblate.org/projects/lukim-gather/server/)

## License

Project is licensed under GPL v3.0
