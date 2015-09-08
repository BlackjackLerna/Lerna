from django.db    import models
from users.models import User

class Problem(models.Model):
    name                 = models.CharField(max_length=255)
    path                 = models.CharField(max_length=255)
    author               = models.CharField(max_length=64, blank=True, db_index=True)
    developer            = models.CharField(max_length=64, blank=True, db_index=True)
    origin               = models.CharField(max_length=128, blank=True, db_index=True)
    description          = models.TextField()
    input_specification  = models.TextField(blank=True)
    output_specification = models.TextField(blank=True)
    samples              = models.TextField(blank=True)
    explanations         = models.TextField(blank=True)
    notes                = models.TextField(blank=True)
    input_file           = models.CharField(max_length=16, blank=True)
    output_file          = models.CharField(max_length=16, blank=True)
    time_limit           = models.PositiveIntegerField()
    memory_limit         = models.PositiveIntegerField()
    checker              = models.CharField(max_length=255)
    mask_in              = models.CharField(max_length=255)
    mask_out             = models.CharField(max_length=255, blank=True)
    analysis             = models.TextField(blank=True)
    created_at           = models.DateTimeField(auto_now_add=True)
    updated_at           = models.DateTimeField(auto_now=True)

    class Meta:
        db_table      = "problems"
        get_latest_by = "created_at"

    @property
    def time_limit_in_secs(self):
        result = self.time_limit / 1000
        return int(result) if result.is_integer() else result

    @time_limit_in_secs.setter
    def time_limit_in_secs(self, value):
        self.time_limit = int(value * 1000)

    def __str__(self):
        return self.name

class Contest(models.Model):
    name          = models.CharField(max_length=255)
    description   = models.TextField(blank=True)
    start_time    = models.DateTimeField(blank=True, null=True)
    duration      = models.PositiveIntegerField(blank=True, null=True)
    freezing_time = models.IntegerField(blank=True, null=True)
    is_school     = models.BooleanField()
    is_admin      = models.BooleanField()
    is_training   = models.BooleanField()
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table      = "contests"
        get_latest_by = "created_at"

    def __str__(self):
        return self.name

class ProblemInContest(models.Model):
    problem    = models.ForeignKey(Problem)
    contest    = models.ForeignKey(Contest)
    number     = models.PositiveIntegerField()
    score      = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table            = "problem_in_contests"
        unique_together     = ("problem", "contest", "number")
        verbose_name_plural = "problems in contest"
        get_latest_by       = "created_at"

    def __str__(self):
        return "{0.contest.id:03}#{0.number}: {0.problem}".format(self)

class Clarification(models.Model):
    # TODO: Replace contest with problem_in_contest.
    contest    = models.ForeignKey(Contest, db_index=False)
    user       = models.ForeignKey(User, db_index=False)
    question   = models.TextField()
    answer     = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table      = "clarifications"
        get_latest_by = "created_at"

    def __str__(self):
        return self.question

class Notification(models.Model):
    # TODO: Fix the DB foreign key.
    contest_id  = models.IntegerField()
    description = models.TextField()
    visible     = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table      = "notifications"
        get_latest_by = "created_at"

    def __str__(self):
        return self.description if len(self.description) <= 100 else self.description[:97] + "..."

class Compiler(models.Model):
    code_name      = models.CharField(max_length=32)
    name           = models.CharField(max_length=255)
    extension      = models.CharField(max_length=255)
    compile_string = models.CharField(max_length=255)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        db_table      = "compilers"
        get_latest_by = "created_at"

    def __str__(self):
        return self.name

class Attempt(models.Model):
    problem_in_contest = models.ForeignKey(ProblemInContest)
    # TODO: Add the DB index.
    user               = models.ForeignKey(User, db_index=False)
    source             = models.TextField()
    compiler           = models.ForeignKey(Compiler)
    time               = models.DateTimeField(auto_now_add=True)
    # TODO: SET NOT NULL DEFAULT = ""
    result             = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    # TODO: SET NOT NULL DEFAULT = ""
    error_message      = models.TextField(blank=True, null=True)
    used_memory        = models.PositiveIntegerField(blank=True, null=True)
    used_time          = models.FloatField(blank=True, null=True)
    score              = models.FloatField(blank=True, null=True)
    # TODO: Remove these three fields.
    lock_version       = models.IntegerField(blank=True, null=True)
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    class Meta:
        db_table      = "attempts"
        get_latest_by = "time"

    def __str__(self):
        return "[{0.id}] {0.problem_in_contest} by {0.user}".format(self)

class TestInfo(models.Model):
    # TODO: Fix the DB foreign key.
    attempt_id  = models.IntegerField()
    test_number = models.PositiveIntegerField()
    result      = models.CharField(max_length=255, blank=True, null=True)
    used_memory = models.PositiveIntegerField(blank=True, null=True)
    used_time   = models.FloatField(blank=True, null=True)

    class Meta:
        db_table        = "test_infos"
        # unique_together = ("attempt_id", "test_number")

    def __str__(self):
        return "{0.attempt_id:05}:{0.test_number}".format(self)
