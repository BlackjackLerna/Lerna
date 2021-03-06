from django.conf.urls import url

from .views import (
    ContestIndexView, TrainingIndexView, TrainingView, ProblemView, AttemptsView,
    AttemptDetailsView, SubmitView, StandingsView, UnfrozenStandingsView, XMLStandingsView,
    UnfrozenXMLStandingsView, ClarificationsView,
)


def _url(regex, cls, name):
    return url(regex, cls.as_view(), name=name)


urlpatterns = (
    _url(r'^$', ContestIndexView, 'contests'),
    _url(r'^trainings/?$', TrainingIndexView, 'trainings'),
    _url(r'^training/(?P<contest_id>\d+)/?$', TrainingView, 'training'),
    _url(r'^(?P<contest_id>\d+)/(?P<problem_number>\d+)/?$', ProblemView, 'problem'),
    _url(r'^(?P<contest_id>\d+)/(?P<problem_number>\d+)/submit/?$', SubmitView, 'submit'),
    _url(r'^(?P<contest_id>\d+)/submit/?$', SubmitView, 'submit'),
    _url(r'^(?P<contest_id>\d+)/attempts/?$', AttemptsView, 'attempts'),
    _url(r'^(?P<contest_id>\d+)/attempts/(?P<page>\d+)/?$', AttemptsView, 'attempts'),
    _url(r'^attempt/(?P<attempt_id>\d+)/?$', AttemptDetailsView, 'attempt'),
    _url(r'^(?P<contest_id>\d+)/standings/?$', StandingsView, 'standings'),
    _url(r'^(?P<contest_id>\d+)/standings\.xml/?$', XMLStandingsView, 'standings-xml'),
    _url(r'^(?P<contest_id>\d+)/unfrozen-standings/?$', UnfrozenStandingsView, 'standings-unfrozen'),
    _url(r'^(?P<contest_id>\d+)/unfrozen-standings\.xml/?$', UnfrozenXMLStandingsView, 'standings-xml-unfrozen'),
    _url(r'^(?P<contest_id>\d+)/clarifications/?$', ClarificationsView, 'clarifications'),
)
