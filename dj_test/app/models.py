from django.db import models
from django_mysql.models import JSONField


class Candidate(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(null=True)
    address = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=15, null=True)
    title = models.CharField(max_length=100, null=True)
    career = JSONField(null=True)
    training = JSONField(null=True)
    cv_ref = models.CharField(max_length=150, null=True)
    # profile summary
    # core skills


class JobOffer(models.Model):
    title = models.CharField(max_length=100)
    owner = models.CharField(max_length=100)
    # eventual fields(salary, requirements ..)
