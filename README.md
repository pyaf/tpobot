# TPO IIT (BHU) Bot

A facebook messenger bot which gives real time updates of [Training and Placement portal](https://placement.iitbhu.ac.in/) of IIT (BHU) to the students. The bot periodically crawls the `company's visit` page and sends private text messages to registered users about new companies according to their branch and course.

The bot uses `Django` as backend framework for webhook, `Celery` as asynchronous task manager, `Redis` as message broker, `Wit` as intent parser, `sqlite3` as database for development on local machine and `postgres` for production on heroku, python's `requests` module for web crawling and `Ngrok` to setup a secure tunnel to localhost for development purposes.

The bot runs three jobs (1 Web server, 1 celery worker and 1 celery beat) on two dynos of heroku. 😎

## Installation 

* Install required dependencies `pip install -r requirements.txt`
* Make sure `redis` is >= 2.10.5, if not, run `pip install celery[redis]`
* Migrate db `python manage.py migrate`
* Start Dev server with `python manage.py runserver`
* Use ngrok with `./ngrok http 8000`
* Start redis-server with `redis-server`
* Run Celery workers with `celery -A tpobot worker -l info` 
* Run Celery beat with `celery -A tpobot beat -l info`


### Set environment variables

* Your server's verify token as `VT`
* FB page access token as `AT`
* TPO username as `username`
* TPO password as `password`
* Wit access token as `wit_server_AT`

### Important Points

* Activate python environment before running `celery`

## Tutorials

  * https://realpython.com/blog/python/asynchronous-tasks-with-django-and-celery/
  * http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html#tut-celery
  * http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html

## Some Help

  * https://stackoverflow.com/a/35481577/6300703

## License: MIT
