# TPO IIT (BHU) Bot

An utterly fantastic facebook messenger bot to give updates of Traning and Placement portal of IIT (BHU).
The project uses `Scrapy` as web crawler, `Django` as backend framework, `Celery` for asynchronous task manager, `Redis` as message broker for celery and `Ngrok` to setup a secure tunnel to localhost for development purposes.

## Installation 

* Install required dependencies `pip install -r requirements.txt`
* Make sure `redis` is >= 2.10.5, if not, run `pip install celery[redis]`
* Start redis-server with `redis-server`
* Use ngrok with `./ngrok http 8000`
* Check celery workers with `celery -A tpobot worker -l info` 
* Migrate db `python manage.py migrate` 
* Crawl TPO portal and store/update Companies' Data in db by `python spider.py`


### Set environment variables

* verify token as `VT`
* access token as `AT`
* TPO username as `username`
* TPO password as `password`

## Tutorials

  * https://realpython.com/blog/python/asynchronous-tasks-with-django-and-celery/
  * http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html#tut-celery
  * http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html

## License: MIT
