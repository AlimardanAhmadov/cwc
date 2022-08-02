web: gunicorn configs.wsgi
celery: celery -A configs.celery worker -l info
celerybeat: celery -A configs beat -l INFO 
celeryworker2: celery -A configs.celery worker & celery -A configs beat -l INFO & wait -n