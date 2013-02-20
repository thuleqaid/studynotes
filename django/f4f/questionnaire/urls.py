from django.conf.urls import patterns, include, url

urlpatterns = patterns('questionnaire.views',
    url(r'^$', 'index'),
    url(r'^(?P<titleid>\d+)/$', 'prelude'),
    url(r'^(?P<titletype>[^/]+)/(?P<titleid>\d+)/$', 'doQuiz'),
)
