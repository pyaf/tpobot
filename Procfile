web: gunicorn tpobot.wsgi
worker: celery worker --app=tpobot.celeryapp
beat: celery -A tpobot beat 
