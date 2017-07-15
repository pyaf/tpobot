# TPO IIT (BHU) Bot

An utterly fantastic facebook messenger bot to give updates of Traning and Placement portal of IIT (BHU).
The project uses `Scrapy` as web crawler, `Django` as backend framework, `Celery` as asynchronous task manager, `Redis` as message broker for celery and `Ngrok` to setup a secure tunnel to localhost for development purposes and `Wit` as intent parser.

## Installation 

* Install required dependencies `pip install -r requirements.txt`
* Make sure `redis` is >= 2.10.5, if not, run `pip install celery[redis]`
* Migrate db `python manage.py migrate`
* Crawl TPO portal and store/update Companies' Data in db by `python spider.py`
* Start Dev server with `python manage.py runserver`
* Use ngrok with `./ngrok http 8000`
* Start redis-server with `redis-server`
* Check celery workers with `celery -A tpobot worker -l info` 


### Set environment variables

* Your server's verify token as `VT`
* FB page access token as `AT`
* TPO username as `username`
* TPO password as `password`
* Wit access token as `wit_server_AT`

## Tutorials

  * https://realpython.com/blog/python/asynchronous-tasks-with-django-and-celery/
  * http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html#tut-celery
  * http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html

## Some Help

  * https://stackoverflow.com/a/35481577/6300703

## License: MIT
