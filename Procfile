web: gunicorn tpobot.wsgi
worker: celery worker --app=tpobot.celeryapp -events -loglevel info
beat: celery -A tpobot beat 
