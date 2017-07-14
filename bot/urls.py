from django.conf.urls import url, include

from .views import *

urlpatterns = [
    url(r'^$', IndexView.as_view()),

    url(r'^f4a09cdd515cb23076a29136a335sdf43df34sdg345s1da5/$', BotView.as_view()),
]
