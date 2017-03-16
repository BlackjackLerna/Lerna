from django.db    import models as md
from django.urls  import reverse
from django.utils import timezone
from users.models import User


class Problem(md.Model):
    name                 = md.CharField(max_length=80)
    path                 = md.CharField(max_length=255)
    author               = md.CharField(max_length=64, blank=True, db_index=True)
    developer            = md.CharField(max_length=64, blank=True, db_index=True)
    origin               = md.CharField(max_length=128, blank=True, db_index=True)
    description          = md.TextField()
    input_specification  = md.TextField(blank=True)
    output_specification = md.TextField(blank=True)
    samples              = md.TextField(blank=True)
    explanations         = md.TextField(blank=True)
    notes                = md.TextField(blank=True)
    input_file           = md.CharField(max_length=16, blank=True)
    output_file          = md.CharField(max_length=16, blank=True)
    time_limit           = md.PositiveIntegerField()
    memory_limit         = md.PositiveIntegerField()
    checker              = md.CharField(max_length=100)
    mask_in              = md.CharField(max_length=32)
    mask_out             = md.CharField(max_length=32, blank=True)
    analysis             = md.TextField(blank=True)
    created_at           = md.DateTimeField(auto_now_add=True)
    updated_at           = md.DateTimeField(auto_now=True)

    class Meta:
        db_table      = 'problems'
        get_latest_by = 'created_at'

    @property
    def time_limit_in_secs(self):
        if self.time_limit % 1000 == 0:
            return self.time_limit // 1000
        else:
            return self.time_limit / 1000

    @time_limit_in_secs.setter
    def time_limit_in_secs(self, value):
        self.time_limit = int(value * 1000 + .5)

    def __str__(self):
        return self.name


class ContestQuerySet(md.QuerySet):
    def privileged(self, user):
        return self if user.is_staff else self.filter(is_admin=False)


class Contest(md.Model):
    name          = md.CharField(max_length=255)
    description   = md.TextField(blank=True)
    start_time    = md.DateTimeField(blank=True, null=True)
    duration      = md.PositiveIntegerField(blank=True, null=True)
    freezing_time = md.IntegerField(blank=True, null=True)
    is_school     = md.BooleanField()
    is_admin      = md.BooleanField()
    is_training   = md.BooleanField()
    created_at    = md.DateTimeField(auto_now_add=True)
    updated_at    = md.DateTimeField(auto_now=True)
    problems      = md.ManyToManyField(Problem, through='ProblemInContest')

    objects = ContestQuerySet.as_manager()

    class Meta:
        db_table      = 'contests'
        get_latest_by = 'created_at'

    @property
    def finish_time(self):
        return self.start_time + timezone.timedelta(minutes=self.duration)

    @property
    def problem_count(self):
        return self.problem_in_contest_set.count()

    @property
    def duration_str(self):
        return '%d:%02d' % divmod(self.duration, 60)

    def __str__(self):
        return self.name if len(self.name) <= 70 else self.name[:67] + '...'

    def get_absolute_url(self):
        # TODO: Replace with something more appropriate.
        return reverse('contests:problem', args=[self.id, 1])

    def is_frozen_at(self, moment):
        freezing_moment = self.start_time + timezone.timedelta(minutes=self.freezing_time)
        return freezing_moment <= moment < self.finish_time

    @classmethod
    def three_way_split(cls, contests, threshold_time):
        """
        Splits the given iterable into three lists: actual, awaiting and past contests,
        regarding the given time point.
        """

        actual = []
        awaiting = []
        past = []
        for contest in contests:
            if contest.start_time > threshold_time:
                awaiting.append(contest)
            elif contest.finish_time <= threshold_time:
                past.append(contest)
            else:
                actual.append(contest)
        return actual, awaiting, past


class PICQuerySet(md.QuerySet):
    def annotate_with_number_char(self):
        return self.annotate(
            number_char=md.Func(
                # ord('A') - 1 == 64
                md.F('number') + 64,
                function='chr',
                output_field=md.CharField(),
            ),
        )

    def is_visible(self, problem):
        return self.filter(problem=problem, contest__is_admin=False).exists()


class ProblemInContest(md.Model):
    problem    = md.ForeignKey(Problem, md.PROTECT)
    contest    = md.ForeignKey(Contest, md.CASCADE)
    number     = md.PositiveIntegerField()
    score      = md.IntegerField(blank=True, null=True)
    # TODO: Remove this field.
    created_at = md.DateTimeField(auto_now_add=True)
    updated_at = md.DateTimeField(auto_now=True)

    objects = PICQuerySet.as_manager()

    class Meta:
        db_table             = 'problem_in_contests'
        default_related_name = 'problem_in_contest_set'
        verbose_name_plural  = 'problems in contest'
        get_latest_by        = 'created_at'

    def __str__(self):
        return '{0.contest.id:03}#{0.number}: "{0.problem}"'.format(self)

    def get_absolute_url(self):
        return reverse('contests:problem', args=[self.contest_id, self.number])


class ClarificationQuerySet(md.QuerySet):
    def privileged(self, user):
        return self if user.is_staff else self.filter(user=user)


class Clarification(md.Model):
    # TODO: Replace contest with problem_in_contest.
    contest    = md.ForeignKey(Contest, md.CASCADE, db_index=False)
    user       = md.ForeignKey(User, md.CASCADE, db_index=False)
    question   = md.TextField()
    answer     = md.TextField(blank=True)
    created_at = md.DateTimeField(auto_now_add=True)
    updated_at = md.DateTimeField(auto_now=True)

    objects = ClarificationQuerySet.as_manager()

    class Meta:
        db_table      = 'clarifications'
        get_latest_by = 'created_at'

    def has_answer(self):
        return bool(self.answer)

    has_answer.boolean = True

    def __str__(self):
        return self.question if len(self.question) <= 70 else self.question[:67] + '...'


class NotificationQuerySet(md.QuerySet):
    def privileged(self, user):
        return self if user.is_staff else self.filter(visible=True, created_at__lte=timezone.now())


class Notification(md.Model):
    contest     = md.ForeignKey(Contest, md.CASCADE)
    description = md.TextField()
    visible     = md.BooleanField(default=True)
    created_at  = md.DateTimeField(auto_now_add=True)
    updated_at  = md.DateTimeField(auto_now=True)

    objects = NotificationQuerySet.as_manager()

    class Meta:
        db_table      = 'notifications'
        get_latest_by = 'created_at'

    def __str__(self):
        return self.description if len(self.description) <= 70 else self.description[:67] + '...'


class Compiler(md.Model):
    name            = md.CharField(max_length=64)
    codename        = md.CharField(max_length=32)
    runner_codename = md.CharField(max_length=32)
    obsolete        = md.BooleanField(default=False)
    # TODO: Remove this field when old tester support is dropped.
    extension       = md.CharField(max_length=255)
    created_at      = md.DateTimeField(auto_now_add=True)
    updated_at      = md.DateTimeField(auto_now=True)
    highlighter     = md.CharField(max_length=32)

    class Meta:
        db_table      = 'compilers'
        get_latest_by = 'created_at'

    def __str__(self):
        return self.name


class Attempt(md.Model):
    problem_in_contest = md.ForeignKey(ProblemInContest, md.CASCADE)
    user               = md.ForeignKey(User, md.CASCADE)
    source             = md.TextField()
    compiler           = md.ForeignKey(Compiler, md.CASCADE)
    time               = md.DateTimeField(auto_now_add=True)
    tester_name        = md.CharField(max_length=48, blank=True, default='')
    # TODO: SET NOT NULL.
    result             = md.CharField(max_length=36, blank=True, null=True, db_index=True)
    error_message      = md.TextField(blank=True, null=True) # NULL for optimization reason.
    # TODO: Make this field an integer (properly converting old attempts).
    used_time          = md.FloatField(blank=True, null=True)
    used_memory        = md.PositiveIntegerField(blank=True, null=True)
    checker_comment    = md.TextField(blank=True, default='')
    score              = md.FloatField(blank=True, null=True)
    # TODO: Remove this field.
    lock_version       = md.IntegerField(blank=True, null=True)
    created_at         = md.DateTimeField(auto_now_add=True)
    updated_at         = md.DateTimeField(auto_now=True)

    class Meta:
        db_table      = 'attempts'
        get_latest_by = 'time'

    @property
    def problem(self):
        return self.problem_in_contest.problem

    @property
    def contest(self):
        return self.problem_in_contest.contest

    @property
    def verdict(self):
        return self.result if self.score is None else '{0.score:.1f}%'.format(self)

    def __str__(self):
        return '[{0.id:05}/{0.problem.id:03}] {0.problem_in_contest} by {0.user}'.format(self)

    def get_absolute_url(self):
        return reverse('contests:attempt', args=[self.id])

    @staticmethod
    def encode_ejudge_verdict(result, score) -> (bytes, int):
        def parse_test(pos):
            try:
                return int(result[pos:])
            except (IndexError, ValueError):
                return 0

        # Sorted by popularity.
        if not result:  # But check for None first.
            return b'PD', 0
        if result.startswith('Wrong answer'):
            return b'WA', parse_test(21)
        if result.startswith('Time limit exceeded'):
            return b'TL', parse_test(28)
        if result.startswith('Runtime error'):
            return b'RT', parse_test(22)
        if result == 'Accepted' or (result == 'Tested' and score > 99.99):
            # FIXME: Number of passed tests should be returned.
            return b'OK', 0
        if result == 'Tested':
            # ditto
            return b'PT', 0
        if result.startswith('Memory limit exceeded'):
            return b'ML', parse_test(30)
        if result == 'Compilation error':
            return b'CE', 0
        if result.startswith('Presentation error'):
            return b'PE', parse_test(27)
        if result.startswith('Security violation'):
            return b'SE', parse_test(27)
        if result.startswith('Idleness limit exceeded'):
            return b'WT', parse_test(32)
        if result == 'Ignored':
            return b'IG', 0
        if result.startswith('Testing'):
            return b'RU', parse_test(11)
        if result in ('Queued', 'Compiling...'):
            return b'CG', 0
        if result.startswith('System error'):
            return b'CF', parse_test(21)
        return b'CF', 0


class TestInfo(md.Model):
    attempt         = md.ForeignKey(Attempt, md.CASCADE)
    test_number     = md.PositiveIntegerField()
    result          = md.CharField(max_length=23, blank=True, default='')
    # TODO: Maybe make these fields non-nullable? TestInfos are immutable anyway.
    used_memory     = md.PositiveIntegerField(blank=True, null=True)
    used_time       = md.FloatField(blank=True, null=True)
    checker_comment = md.TextField(blank=True, default='')

    class Meta:
        db_table        = 'test_infos'
        # unique_together = ('attempt_id', 'test_number')

    def __str__(self):
        return '{0.attempt_id:05}:{0.test_number}'.format(self)
