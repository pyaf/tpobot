web: gunicorn tpobot.wsgi
worker: celery worker --app=tpobot.celeryapp -loglevel info
beat: celery -A tpobot beat 
