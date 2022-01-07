from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import random, string

class Quiz(models.Model):
    """A quiz is owned by a user and contains questions."""
    title = models.CharField(max_length=1024)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    code = models.CharField(max_length=8, default=None)  # hard-to-guess LETTER-code used for quiz URL

    def save(self, *args, **kwargs):
        """ On save, update timestamps and generate code"""
        if not self.id:
            self.created = timezone.now()
        # if we don't have a code, generate a unique one
        while not self.code:
            code = ''.join(random.choices(string.ascii_uppercase, k=4))
            if Quiz.objects.filter(code=code).count() == 0:
                self.code = code
        self.modified = timezone.now()
        return super(Quiz, self).save(*args, **kwargs)


class Question(models.Model):
    """A question belongs to a quit, has a question text, is active or not and keeps some timestamps."""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.CharField(max_length=1024)
    active = models.BooleanField(default=False)  # is the question active in its quiz?
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()  # starting and stopping are modifications as well
    started = models.DateTimeField(null=True)  # TODO: currently unused
    started_times = models.IntegerField(default=0)  # how many times has the question been started

    def save(self, *args, **kwargs):
        """On save, update timestamps"""
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        # call superclass
        return super(Question, self).save(*args, **kwargs)

    def start(self):
        """Starts a question"""
        self.active = True
        self.started = timezone.now()
        self.started_times += 1
        self.save()

    def stop(self):
        """Stops a question"""
        self.active = False
        self.save()

    def reset(self):
        """Resets a question"""
        self.answer_set.all().delete()
        self.active = False
        self.started_times = 0
        self.save()


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    username = models.CharField(max_length=1024)
    answer = models.CharField(max_length=1024)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Answer, self).save(*args, **kwargs)
