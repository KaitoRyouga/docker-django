# How to run?

## Build container
> docker-compose -f docker-compose.prod.yml up -d

---

## Build static file
> docker exec -it docker-django_web_1 python manage.py collectstatic --noinput
