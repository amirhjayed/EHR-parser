from django.contrib import admin

from .models import Recruiter, JobOffer, Candidate


# class QuestionAdmin(admin.ModelAdmin):
#     fields = ['pub_date', 'question_text']


admin.site.register(Recruiter)
admin.site.register(JobOffer)
admin.site.register(Candidate)
