from django.shortcuts import get_object_or_404, render
from django.views     import generic

from django.db.models import IntegerField, Count, Case, When, Q, F
from core.models import Problem, Contest, ProblemInContest, Attempt
from users.models import User

import datetime
import pytz

class RatingIndexView(generic.ListView):
    context_object_name = 'user_list'
    queryset = (
    	User.objects.all().annotate(
            rating=Count(
                Case(
            	    When(attempt__problem_in_contest__contest__is_admin=True, then=None),
                    When(attempt__result='Accepted', then=F('attempt__problem_in_contest__problem_id')),
                    When(Q(attempt__result='Tested') & Q(attempt__score='100'), then=F('attempt__problem_in_contest__problem_id')),
                    default=None,
                ), distinct=True
            )
        )
        .exclude(rating=0)
    )

    tst = (
    ProblemInContest.objects
        .select_related('attempt')
        .select_related('users')
        .select_related('problems')
        .select_related('contests')
        .annotate(Count('problem', distinct=True))
    )

    ordering = "-rating"
    template_name = "global_statistics/rating.html"
    allow_empty = True
    paginate_by = 25
    paginate_orphans = 1