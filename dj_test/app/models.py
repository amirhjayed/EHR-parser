from django.db import models
from django_mysql.models import JSONField


class Candidate(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    career = JSONField()
    training = JSONField()
    cv_ref = models.FileField()
    # profile summary
    # core skills


class JobOffer(models.Model):
    title = models.CharField(max_length=100)
    owner = models.CharField(max_length=100)
    # eventual fields(salary, requirements ..)
