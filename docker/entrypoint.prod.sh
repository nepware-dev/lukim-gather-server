#!/bin/sh
if [ "$CELERY_WORKER" = "true" ]
then
    if [ -z "$CELERY_QUEUES" ]
    then
        uv run celery -A lukimgather worker -l info
    else
        uv run celery -A lukimgather worker -l info -Q "$CELERY_QUEUES"
    fi
else
    uv run ./manage.py migrate --no-input
    uv run ./manage.py import_default_email_template
    uv run ./manage.py createinitialrevisions
    uv run gunicorn lukimgather.asgi:application -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
fi
