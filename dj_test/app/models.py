from django.db import models
from django_mysql.models import JSONField
from django.contrib.auth.models import User


class Recruiter(models.Model):
    name = models.CharField(max_length=50)
    domain = models.CharField(max_length=50, null=True)
    email = models.EmailField(null=True, unique=True)
    phone = models.CharField(max_length=15, null=True)
    location = models.CharField(max_length=200, null=True)
    summary = models.TextField(null=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return "%s" % (self.name)


class JobOffer(models.Model):
    title = models.CharField(max_length=100)
    schedule = models.CharField(max_length=20, null=True)
    salary = models.CharField(max_length=20, null=True)
    degree = models.CharField(max_length=50, null=True)
    experience = models.IntegerField(default=0)
    programming_languages = models.CharField(max_length=100, null=True, blank=True)
    frameworks = models.CharField(max_length=100, null=True, blank=True)
    languages = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True)
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "%s" % (self.title)


class Candidate(models.Model):
    name = models.CharField(unique=True, max_length=50)
    email = models.EmailField(unique=True, null=True)
    address = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=15, null=True)
    title = models.CharField(max_length=100, null=True)
    programming_languages = models.CharField(max_length=200, null=True)
    programming_frameworks = models.CharField(max_length=200, null=True)
    languages = models.CharField(max_length=200, null=True)
    degree = models.CharField(max_length=50, null=True)
    experience = models.IntegerField(default=0)
    career = JSONField(null=True)
    training = JSONField(null=True)
    cv_ref = models.CharField(max_length=150, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "%s" % (self.name)
