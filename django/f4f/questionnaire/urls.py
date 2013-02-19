from django.conf.urls import patterns, include, url

urlpatterns = patterns('questionnaire.views',
    url(r'^$', 'index'),
    url(r'^(?P<titleid>\d+)/$', 'doTest'),
)
