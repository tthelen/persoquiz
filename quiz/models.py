from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import random, string

class Quiz(models.Model):
    title = models.CharField(max_length=1024)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    code = models.CharField(max_length=8, default=None)

    def save(self, *args, **kwargs):
        """ On save, update timestamps """
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
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.CharField(max_length=1024)
    active = models.BooleanField(default=False)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    started = models.DateTimeField(null=True)
    started_times = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Question, self).save(*args, **kwargs)


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
