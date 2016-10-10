from django.shortcuts          import get_object_or_404, render, redirect
from django.views.generic      import TemplateView
from django.views.generic.edit import FormView
from django                    import forms

from core.models import Contest, ProblemInContest, Attempt, Compiler

import datetime
import pytz

import os


class ContestIndexView(TemplateView):
    template_name = 'contests/contests.html'

    def get_context_data(self, **kwargs):
        def get_contests():
            time_now = datetime.datetime.now(pytz.timezone('US/Pacific'))  # TODO: not US/Pacific! Use local settings
            contests = Contest.objects.filter(is_training=False)
            actual = []
            wait = []
            past = []
            for contest in contests:
                if time_now < contest.start_time:
                    wait.append(contest)
                elif contest.start_time + datetime.timedelta(minutes=contest.duration) < time_now:
                    past.append(contest)
                else:
                    actual.append(contest)
            return actual, wait, past

        context = super().get_context_data(**kwargs)
        context['actual_contest_list'], context['wait_contest_list'], context['past_contest_list'] = get_contests()
        return context


class TrainingIndexView(TemplateView):
    template_name = 'contests/trainings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trainings_raw = (
            Contest.objects.filter(is_training=True)
            .order_by("name")
        )

        trainings = []
        cur_prefixes = []

        for t in trainings_raw:
            name_parts = t.name.split('/')

            cur_prefixes = os.path.commonprefix([name_parts, cur_prefixes])
            idx = len(cur_prefixes)

            while idx < len(name_parts):
                if idx == len(name_parts) - 1:
                    trainings.append({'tab': ' '*idx, 'is_terminal': True, 'id': t.id, 'name': name_parts[idx]})
                else:
                    cur_prefixes.append(name_parts[idx])
                    trainings.append({'tab': ' '*idx, 'is_terminal': False, 'id': None, 'name': name_parts[idx]})
                idx += 1

        context.update(trainings=trainings)
        return context


class TrainingView(TemplateView):
    template_name = 'contests/training.html'

    def get_context_data(self, *, contest_id, **kwargs):
        context = super().get_context_data(id=contest_id, **kwargs)
        training = Contest.objects.get(id=contest_id)
        pics = (
            ProblemInContest.objects
            .filter(contest=training)
            .order_by("number")
            .select_related("problem")
        )
        context.update(contest=training, pics=pics)
        return context


class SubmitForm(forms.Form):
    def __init__(self, contest_id, *args, **kwargs):
        super(SubmitForm, self).__init__(*args, **kwargs)

        self.fields['compiler'] = forms.ChoiceField(
            choices=[(compiler.id, compiler.name) for compiler in Compiler.objects.all()]
        )

        contest = Contest.objects.get(id=contest_id)
        pics = (
            ProblemInContest.objects
                .filter(contest=contest)
                .order_by("number")
                .select_related("problem")
        )
        self.fields['problem'] = forms.ChoiceField(
            choices=[(pic.id, '{0} {1}'.format(pic.number, pic.problem.name)) for pic in pics]
        )

        self.fields['source'] = forms.CharField(widget=forms.Textarea)


class SubmitView(FormView):
    template_name = 'contests/submit.html'
    form_class = SubmitForm

    def get(self, request, *args, **kwargs):
        contest_id = self.kwargs['contest_id']
        contest = Contest.objects.get(id=contest_id)
        form = self.form_class(contest_id)
        return render(request, self.template_name, {'form': form, 'contest': contest})

    def post(self, request, *args, **kwargs):
        contest_id = self.kwargs['contest_id']
        contest = Contest.objects.get(id=contest_id)
        form = self.form_class(contest_id, request.POST)
        if form.is_valid():
            Attempt.objects.create(
                user_id=self.request.user.id,
                problem_in_contest_id=form.cleaned_data['problem'],
                compiler_id=form.cleaned_data['compiler'],
                source=form.cleaned_data['source'],
            )
            return redirect('/contests/attempts/{0}'.format(contest_id))
        return render(request, self.template_name, {'form': form, 'contest': contest})


class AttemptsView(TemplateView):
    template_name = 'contests/attempts.html'

    def get_context_data(self, *, contest_id, **kwargs):
        context = super().get_context_data(id=contest_id, **kwargs)
        contest = Contest.objects.get(id=contest_id)
        if self.request.user.is_authenticated():
            attempts = (
                Attempt.objects
                    .filter(problem_in_contest__contest=contest)
                    .filter(user_id=self.request.user.id)
                    .order_by("-time")
                    .select_related("problem_in_contest")
                    .select_related("compiler")
            )
        else:
            attempts = None
        context.update(contest=contest, attempts=attempts)
        return context


class SourceView(TemplateView):
    template_name = 'contests/source.html'

    def get_context_data(self, *, attempt_id, **kwargs):
        context = super().get_context_data(id=attempt_id, **kwargs)
        contest = None
        if self.request.user.is_authenticated():
            attempt = Attempt.objects.get(id=attempt_id)
            if attempt is not None:
                contest = Contest.objects.get(id=attempt.problem_in_contest.contest_id)
        else:
            attempt = None
        context.update(contest=contest, attempt=attempt)
        return context


class ErrorsView(TemplateView):
    template_name = 'contests/errors.html'

    def get_context_data(self, *, attempt_id, **kwargs):
        context = super().get_context_data(id=attempt_id, **kwargs)
        contest = None
        if self.request.user.is_authenticated():
            attempt = Attempt.objects.get(id=attempt_id)
            if attempt is not None:
                contest = Contest.objects.get(id=attempt.problem_in_contest.contest_id)
        else:
            attempt = None
        context.update(contest=contest, attempt=attempt)
        return context
